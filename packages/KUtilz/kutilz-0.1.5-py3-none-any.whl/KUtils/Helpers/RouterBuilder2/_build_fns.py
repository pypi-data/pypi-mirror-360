import dataclasses

from KUtils.Typing import *

@dataclasses.dataclass
class RouterBuildingContexts:
    children: Dict[int, Any]
    _child_routers_buffer: List[Any] = []

def create_router(router_ctor: Type[T], target, contexts: RouterBuildingContexts) -> T:
    pass