from fp_admin.apps.auth.models import User, Group
from fp_admin.core.models.base import AdminModel


class UserAdmin(AdminModel):
    model = User
    label = "User of App"


class GroupAdmin(AdminModel):
    model = Group
    label = "Group of users"
