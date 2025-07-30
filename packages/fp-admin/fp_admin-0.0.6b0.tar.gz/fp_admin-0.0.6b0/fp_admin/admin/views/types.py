from typing import List, Literal

from pydantic import BaseModel

from fp_admin.admin.fields import FieldView


class BaseView(BaseModel):
    name: str
    view_type: Literal["form", "list"]
    model: str
    fields: List[FieldView]


class FormView(BaseView):
    view_type: Literal["form"] = "form"


class ListView(BaseView):
    view_type: Literal["list"] = "list"
    default_form_id: str
