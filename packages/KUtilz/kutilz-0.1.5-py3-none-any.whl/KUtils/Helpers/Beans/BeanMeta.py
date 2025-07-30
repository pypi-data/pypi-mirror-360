from __future__ import annotations
import dataclasses
import functools

from KUtils.Typing import *
from KUtils.Helpers.DataClass import DataClass
from KUtils.Helpers.Argpack import Argspec

class BeanException(Exception):
    pass

class DependencyResolutionFailure(BeanException):
    pass

@dataclasses.dataclass
class BeanMeta:
    parent: NotRequired[Self]
    qualifiers: Set[str]
    type: type
    ctor: callable
    argspec: Argspec
    id: str

    @property
    def defaults(self) -> dict:
        return self.argspec.name2defaults
    
    @functools.cached_property
    def dependencies(self) -> Dict[str, Type]:
        return self.argspec.name2type

    def __hash__(self):
        return self.id

    @property
    def all_qualifiers(self) -> Set[str]:
        if self.parent is not None:
            return {**self.qualifiers, **self.parent.qualifiers}
        else:
            return self.qualifiers

    def __repr__(self):
        return f'[BeanDef][type:{self.type}][names:{self.qualifiers}]'

_VALUE_TYPES = (int, str, float, bool, Literal)

class BeanRepositoryBuilder:
    def __init__(self, name: str):
        self.name = name
        self.__repo: Dict[type, BeanMeta] = {}
        self.__namerepo: Dict[str, BeanMeta] = {}
        self.__literals: Dict[str, Dict[str, Any]] = {}
        self.__instances: Dict[BeanMeta, object] = {}

    def beandef(self, ident) -> Optional[BeanMeta]:
        if isinstance(ident, str):
            beandef = self.__namerepo.get(ident, None)
        elif isinstance(ident, type):
            beandef = self.__repo.get(ident, None)
            if beandef is not None:
                beandef = self.__namerepo.get(list(beandef.qualifiers)[0])
        else:
            raise TypeError(f'Bad argument type {type(ident)}')
        return beandef

    @overload
    def __call__(self, ident: str, detached: bool = False, throws = True, **kwargs) -> object: pass
    @overload
    def __call__(self, ident: Type[T], detached: bool = False, throws = True, **kwargs) -> T: pass
    def __call__(self, ident: str | Type[T], detached: bool = False, throws = True, **kwargs) -> object | T:
        beandef = self.beandef(ident)

        if beandef is None:
            if throws is False:
                return None
            else:
                raise DependencyResolutionFailure(f'Cannot find beandef with {ident}')

        instance = self.__instances.get(beandef, None)

        if detached is True:
            return self.instantiate(beandef)
        elif instance is None:
            instance = self.instantiate(beandef)
            self.__instances[beandef] = instance

        return instance

    getbean = __call__

    def instantiate(self, beandef: BeanMeta):
        args = self.resolv_args(beandef)
        argpack = beandef.argspec.kwargs_to_argpack(args)
        args = beandef.argspec.coarse(*argpack.args, **argpack.kwargs)
        return beandef.ctor(*args.args, **args.kwargs)


    def __find_parent(self, bean_fn) -> BeanMeta | None:
        if not isinstance(bean_fn, type):
            return None
        else:
            return self.__repo.get(bean_fn.mro()[1], None)

    def alias(self, alias: str, target_ident):
        beandef = self.beandef(target_ident)
        self.__namerepo[alias] = beandef
        beandef.qualifiers.add(alias)

    def inject_deps(self, ident: str, deps: dict):
        # beandef = self.beandef(ident)
        for name, val in deps.items():
            self.inject_literal(ident, name, val)


    def register(self, bean_fn: Callable | type, *, name: str = None, env: str = None):
        argspec = Argspec.Extract(bean_fn)
        for _n, _t in argspec.name2type.items():
            if _n not in {'args', 'self', 'kwargs'}:
                assert _t not in (Any, None), f'Error registering Bean {bean_fn}, type annotation is required for arg {_n}, got {_t}.'

        ctor = bean_fn
        qualifiers = set([name or bean_fn.__name__])
        if callable(bean_fn):
            assert argspec.ret not in (None, Any), f'Bean functions must have return annotations.'
            t = argspec.ret
        elif isinstance(bean_fn, type):
            t = bean_fn
        else:
            raise TypeError(f'Bad bean initializer type {type(bean_fn)}')

        parent=self.__find_parent(bean_fn)

        beandef = BeanMeta(parent=parent,
                           qualifiers=qualifiers,
                           type=t,
                           ctor=ctor,
                           argspec=argspec,
                           id=len(self.__repo))

        for qual in beandef.all_qualifiers:
            if self.__namerepo.get(qual, None) not in (None, beandef.parent):
                raise ValueError(f'Conflict in setting Bean alias {qual}')
            self.__namerepo[qual] = beandef

        self.__repo[beandef.type] = beandef

        return bean_fn

    def inject_literal(self, target_name: str, key: str, val: Any):
        d = self.__literals.setdefault(target_name, {})
        d[key] = val

    def resolv_arg(self, beandef: BeanMeta, key: str, t: type):
        if t in _VALUE_TYPES:
            for alias in beandef.qualifiers:
                res = self.__literals.get(alias, {}).get(key, None)
                if res is not None:
                    return res
            raise KeyError(f'Cannot find dependency {key} for {beandef}')
        else:
            val = self.getbean(t, throws=False)
            if val is None:
                val = self.getbean(key, throws=False)
                if val is None:
                    raise DependencyResolutionFailure(f'Cannot resolve dependency from neither type {type} nor name {key}!')

            return val
        
    def resolv_args(self, beandef: BeanMeta):
        try:
            args = {}
            for key, t in beandef.dependencies.items():
                try:
                    args[key] = self.resolv_arg(beandef, key, t)
                except:
                    if key in beandef.defaults:
                        args[key] = beandef.defaults[key]
                    else:
                        raise
            return args
        except DependencyResolutionFailure as e:
            raise DependencyResolutionFailure(beandef, e)

    def tget(self, t: type) -> object:
        beandef = self.__repo.get(t, None)
        if None is beandef:
            raise ValueError(f'Bean for type {t} is not found!')

    def hasbean(self, ident):
        return ident in self.__namerepo or ident in self.__repo

    def Bean(self, name: str = None, env: str = 'all'):
        return functools.partial(self.register, name=name, env=env)

    def Autowire(self, name: str = None):
        def _wrap(fn: Callable[[None], T]):
            if name is None:
                from KUtils import Argspec
                argspec = Argspec.Extract(fn)
                assert argspec.ret not in [None, Any]
                ident = argspec.ret
            else:
                ident = name

            return property(fget=lambda x : self.getbean(ident))
        return _wrap
    
    
