from fp_admin.admin.models import AdminModel
from fp_admin.apps.auth.models import Group, User


class UserAdmin(AdminModel):
    model = User
    label = "User of App"


class GroupAdmin(AdminModel):
    model = Group
    label = "Group of users"
