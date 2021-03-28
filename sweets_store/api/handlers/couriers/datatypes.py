import typing as t

from pydantic import BaseModel, root_validator, validator

from sweets_store.utils.dates import pydantic_match_hours_interval_validator

from .constants import CouriersTypes


class CourierCreateModel(BaseModel):
    courier_id: int
    courier_type: CouriersTypes
    regions: t.List[int]
    working_hours: t.List[str]

    _match_hours_interval = validator("working_hours", allow_reuse=True, each_item=True)(
        pydantic_match_hours_interval_validator
    )


class CourierPatchModel(BaseModel):
    courier_id: int
    courier_type: t.Optional[CouriersTypes]
    regions: t.Optional[t.List[int]]
    working_hours: t.Optional[t.List[str]]

    _match_hours_interval = validator("working_hours", allow_reuse=True, each_item=True)(
        pydantic_match_hours_interval_validator
    )

    @root_validator(pre=True)
    def check_provided_values(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """Check that all provided fields are described and valid"""

        error_message = "Fields that are provided but ended up as 'None's after validation: "
        empty_keys = []

        for key, value in values.items():
            if value is None:
                empty_keys.append(key)

        if empty_keys:
            raise ValueError(error_message + ", ".join(empty_keys))

        return values
