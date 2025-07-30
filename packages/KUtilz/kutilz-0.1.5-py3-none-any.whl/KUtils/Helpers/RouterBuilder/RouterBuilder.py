import copy
import types
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from KUtils.Typing import *
from KUtils.Helpers.Argpack import Argspec, PydanticArgspec
from anytree import NodeMixin, RenderTree
from KUtils.Helpers.Strenum import Strenum
__all__ = ['RouterBuilder']

def sanitize_path(path: str):
    if path == '/':
        return path
    else:
        return path.removeprefix('/').removesuffix('/')

@dataclass
class RouteConfig:
    path: str
    description: str = ""
    aliases: List[str] = None
    logical_parent: str = None
    logical_route: str = None
    name: str = None
    metadata: dict = None

    def __post_init__(self):
        self.path = sanitize_path(self.path)
        if isinstance(self.aliases, str):
            self.aliases = [self.aliases]

_INJ = '___IS_ROUTE_KUTILS'

def IsRoute(target, key=_INJ):
    return getattr(target, key, False) is not False

def GetRoute(target, key=_INJ):
    assert IsRoute(target, key)
    return getattr(target, key, False)

def SetRoute(target, route, key=_INJ):
    setattr(target, key, route)

class TargetType(Strenum):
    METHOD = 'method'
    FUNCTION = 'function'
    CLASS = 'class'
    EMPTY = 'empty'


class DefaultRouteHandler:
    def _resolve_handler(self, target):
        if isinstance(target, type):
            return target.__call__
        elif callable(target):
            return target
        else:
            return None

    def __init__(self, target):
        self.target = target
        self.handler = self._resolve_handler(target)

        if self.handler is not None:
            argspec = Argspec.Extract(self.handler, False)
            if isinstance(target, type):
                _type = TargetType.CLASS
            elif argspec.pos_count > 0 and argspec.by_pos(0).name == 'self':
                _type = TargetType.METHOD
            else:
                _type = TargetType.FUNCTION
        else:
            argspec = None
            _type = TargetType.EMPTY

        self.type = _type
        self.spec = argspec

    def __call__(self, *args, **kwargs):
        try:
            return self.spec.coarse(*args, **kwargs).call(self.handler)
        except:
            raise

class ConstructorRouteHandler(DefaultRouteHandler):
    def _resolve_handler(self, target):
        if isinstance(target, type):
            return target
        else:
            return None

    def __init__(self, target):
        super().__init__(target)
        self.handler = target
        self.spec = PydanticArgspec.Extract(target, False)


class Route(NodeMixin):
    children: List['Route']
    siblings: List['Route']
    ancestors: List['Route']
    parent: 'Route'

    @classmethod
    def ExtractRoute(cls, target) -> Optional[Self]:
        if IsRoute(target):
            return GetRoute(target)
        else:
            return None

    @property
    def prototype(self) -> Type[Self]:
        return self.root.__class__.__dict__.get('__BaseRoute__')

    @classmethod
    def Empty(cls, path: str) -> Self:
        return cls(
            RouteConfig(
                path=path
            ),
            None
        )

    @classmethod
    def Empties(cls, paths: List[str]) -> List[Self]:
        nodes = [cls.Empty(path) for path in paths]
        for i in range(len(nodes) - 1):
            nodes[i] << nodes[i + 1]
        return nodes

    def __bind_children__(self):
        cls = self.handler.target
        for name in dir(cls):
            attr = getattr(cls, name)
            if IsRoute(attr):
                self << GetRoute(attr)

    def __post_init__(self):
        pass

    def __invoke__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def __activate__(self, *args, **kwargs):
        pass

    def __init__(self,
                 config: RouteConfig,
                 object: Any,
                 children: List['Route'] = None,
                 parent: 'Route' = None):
        super().__init__()
        self.config = config
        self.handler = DefaultRouteHandler(object)
        self.parent = parent
        self.otype = self.handler.type
        self.children_dict ={}

        if object is not None:
            SetRoute(object, self)

        if children is None:
            children = []
        self.children: List['Route'] = children
        self.__post_init__()

    def route(self, path: str = None, desc: str = "", aliases: Union[str, List[str]] = None, **kwargs):
        def descriptor(target):
            nonlocal path
            if path is None:
                path = target.__name__.lower()

            config = RouteConfig(path, desc, aliases=aliases, metadata=kwargs)

            # print('Creating route with config,', config, 'Parent is: ', self)

            child = self.prototype(config, target)

            child.__bind_children__()

            self << child
            return target
        return descriptor

    def __contains__(self, name: str):
        return name in self.children_dict

    def __setitem__(self, key, value):
        self.children_dict[key] = value

    def __getitem__(self, item) -> Self:
        return self.children_dict[item]

    def __delitem__(self, key):
        del self.children_dict[key]

    def cget(self, name: str) -> Union[Self, None]:
        return self.children_dict.get(name, None)

    def _post_attach(self, parent):
        parent[self.name] = self

    def _post_detach(self, parent):
        del parent[self.name]

    def _pre_attach(self, parent):
        if self.name in parent:
            if parent[self.name].otype != TargetType.EMPTY:
                raise ValueError(f'Path {self.name} already exists in router')


    def __lshift__(self, other: 'Route'):
        if isinstance(other, Route):
            other.parent = self
        elif isinstance(other, list):
            for o in other:
                self << other
        else:
            raise TypeError(f'{type(other)}')

    @property
    def name(self) -> str:
        return f'{self.config.path}'

    @property
    def route_path(self) -> Path:
        if self.is_root:
            return Path('/')
        else:
            return self.parent.route_path / self.name

    @property
    def node_path(self):
        return self.path

    def __repr__(self):
        return self.name

    def render(self) -> RenderTree:
        return RenderTree(self)

    def on_finalize(self):
        pass

    def __route_tree(self):
        if not self.is_root:
            raise Exception()
        PROTOTYPE = self.prototype

        new_root = PROTOTYPE(config=self.config, object=self.handler.target)

        def sanitized_add(child: Self):
            parent = new_root
            paths = str(child.route_path).split('/')
            paths = [p for p in paths if p != '']

            if len(paths) > 1:
                _empties = Route.Empties(paths[:-1])
                for _empty in _empties:
                    if _empty.name not in parent:
                        parent << _empty
                        parent = _empty
                    else:
                        parent = parent[_empty.name]

            new_config = copy.deepcopy(child.config)
            new_config.path = paths[-1]
            new_config.logical_route = str(child.route_path)
            new_config.logical_parent = str(child.parent.route_path)

            new_child = PROTOTYPE(config=new_config, object=child.handler.target)
            self.logical_routes[new_config.logical_route] = new_child

            parent << new_child

        for child in self.descendants:
            sanitized_add(child)

        self.children = []
        self.children = new_root.children
        return self

    def sanitize(self):
        self.__route_tree()

    @final
    def finalize(self, cb=None, verbose: bool = False):
        if verbose:
            print(f'====Bolter Client Finalization Started')
            print(self.render())

        if self.is_root:
            self.sanitize()
            cb = self.__class__.__dict__.get('on_finalize', lambda x: 1)

        cb(self) # todo: deprecate
        self.__finalize__()
        
        for child in self.children:
            child.finalize(cb, False)

        if verbose:
            print(f'====Bolter Client Finalization Ended')
            print(self.render())
    
    def __finalize__(self):
        pass
    
    @final
    def activate(self, *args, **kwargs):
        return self.__activate__(*args, **kwargs)

    @final
    def invoke(self, *args, **kwargs):
        return self.__invoke__(*args, **kwargs)

    def route_find(self, paths, verbose=True) -> Tuple[Union['Route', None], int]:
        next = self
        i = 0

        for i, path in enumerate(paths):
            _next = next.cget(path)
            if _next is None:
                return next, i - 1
            else:
                next = _next
        
        return next, i
    

    @property
    def root(self) -> 'RouterBuilder':
        return super().root

    @property
    def logical_path(self) -> str:
        return self.config.logical_route

    @property
    def logical_parent(self) -> Optional[Self]:
        logical_parent_path = self.config.logical_parent
        return self.root.logical_routes.get(logical_parent_path, None)

    @property
    def logical_ancestors(self) -> Iterator[Self]:
        while self.logical_parent is not None:
            self = self.logical_parent
            yield self

    @property
    def target(self):
        return self.handler.target

class RouterBuilder(Route):
    def __init_subclass__(cls, **kwargs):
        assert cls.__dict__.get('__BaseRoute__') is not None

    class Handlers:
        Default = DefaultRouteHandler
        Constructor = ConstructorRouteHandler

    Route = Route

    __BaseRoute__ = Route

    def __init__(self, name: str, object: T):
        self.logical_routes = {}
        super().__init__(
            RouteConfig(f'/{name}', name=name), object
        )