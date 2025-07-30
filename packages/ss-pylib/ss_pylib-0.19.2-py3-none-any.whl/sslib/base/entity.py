from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from sslib.base.dict import DictEx


@dataclass_json
class JsonEntity:
    pass


# NOTE
# @dataclass_json 데코레이터만 사용하면 schema() 오류 발생,
# DataClassJsonMixin과 함께 사용해서 막는다 (좋은 방법은 아닌듯)
@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
class JsonCamelEntity(DataClassJsonMixin):
    pass


@deprecated('CamelEntity 사용')
@dataclass
class Entity(DictEx):
    pass


@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
