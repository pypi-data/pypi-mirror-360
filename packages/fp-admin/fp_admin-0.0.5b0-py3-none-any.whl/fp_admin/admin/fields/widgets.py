"""
Widget types for fp-admin.

This module defines the widget types that can be used to render different field types
in the admin interface.
"""

from typing import Literal, Union

# Widget types for different field types
TextWidget = Literal["text", "email", "password", "search", "tel", "url"]
NumberWidget = Literal["number", "range", "slider"]
DateWidget = Literal["date", "datetime-local", "time", "month", "week"]
SelectWidget = Literal["select", "radio", "checkbox-group", "autocomplete"]
MultiSelectWidget = Literal["multi-select", "checkbox-group", "tags", "chips"]
FileWidget = Literal["file", "image", "document"]
TextareaWidget = Literal["textarea", "richtext", "markdown"]
BooleanWidget = Literal["checkbox", "toggle", "switch"]

# Union of all widget types
WidgetType = Union[
    TextWidget,
    NumberWidget,
    DateWidget,
    SelectWidget,
    MultiSelectWidget,
    FileWidget,
    TextareaWidget,
    BooleanWidget,
]

# Default widget mappings for field types
DEFAULT_WIDGETS: dict[str, WidgetType] = {
    "text": "text",
    "number": "number",
    "date": "date",
    "checkbox": "checkbox",
    "radio": "radio",
    "select": "select",
    "textarea": "textarea",
    "file": "file",
    "relationship": "select",
}
