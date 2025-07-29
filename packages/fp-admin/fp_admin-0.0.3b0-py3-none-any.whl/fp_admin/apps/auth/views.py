from fp_admin.apps.auth.models import User
from fp_admin.core.views.builder import BaseViewBuilder
from fp_admin.core.views.field_spec import FormField


class UserFormView(BaseViewBuilder):
    model = User
    view_type = "form"
    name = "UserForm"
    fields = [
        FormField(name="username", label="Username", field_type="text"),
        FormField(name="email", label="Email", field_type="text"),
        FormField(name="is_active", label="Is Active", field_type="text"),
    ]


class UserListView(BaseViewBuilder):
    model = User
    view_type = "list"
    name = "UserList"
    # fields = [
    #     FormField(name="username", label="Username", field_type="text"),
    #     FormField(name="email", label="Email", field_type="text"),
    # ]
    #
