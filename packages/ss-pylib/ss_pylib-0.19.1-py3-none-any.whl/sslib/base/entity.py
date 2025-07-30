from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import LetterCase, dataclass_json
from sslib.base.dict import DictEx


@dataclass_json
class JsonEntity:
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
class JsonCamelEntity:
    pass


@deprecated('CamelEntity 사용')
@dataclass
class Entity(DictEx):
    pass


@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
