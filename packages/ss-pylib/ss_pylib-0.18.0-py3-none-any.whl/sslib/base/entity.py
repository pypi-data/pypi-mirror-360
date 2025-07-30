from dataclasses import dataclass, field
from sslib.base.dict import DictEx


@dataclass
class Entity(DictEx):
    pass


@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
