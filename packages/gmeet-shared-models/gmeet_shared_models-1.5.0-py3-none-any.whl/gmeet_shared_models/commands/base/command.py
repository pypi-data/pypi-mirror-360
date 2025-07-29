from typing_extensions import Annotated
from pydantic import BaseModel, Field, AfterValidator
from .type import CommandType


class BaseCommand(BaseModel):
    type: Annotated[
        CommandType,
        Field(
            init=False, description="This field must be overridden by all subclasses"
        ),
        AfterValidator(
            lambda v: v
            if v is not None
            else ValueError("Field 'type' must be overridden in subclasses")
        ),
    ]
