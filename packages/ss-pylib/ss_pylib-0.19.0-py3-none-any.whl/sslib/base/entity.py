from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import DataClassJsonMixin, LetterCase
from sslib.base.dict import DictEx


class JsonCamelMixin(DataClassJsonMixin):
    class Config:
        letter_case = LetterCase.CAMEL


@dataclass
class JsonEntity(DataClassJsonMixin):
    pass


@dataclass
class JsonCamelEntity(JsonCamelMixin):
    pass


@deprecated('CamelEntity 사용')
@dataclass
class Entity(DictEx):
    pass


@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
