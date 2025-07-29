from typing import List, Union, Optional, Literal

from pydantic import BaseModel

FieldType = Literal[
    "text", "number", "date", "checkbox", "radio", "select", "textarea", "Any"
]


class FieldOption(BaseModel):
    label: str
    value: Union[str, bool, int]


class FieldError(BaseModel):
    code: str
    message: str


class FormField(BaseModel):
    name: str
    label: str
    help_text: Optional[str] = None
    field_type: FieldType
    options: Optional[List[FieldOption]] = None
    error: Optional[FieldError] = None
