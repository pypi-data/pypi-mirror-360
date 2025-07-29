from fp_admin.core.views.base import BaseViewFactory
from fp_admin.core.views.types import FormView, ListView


class FormViewFactory(BaseViewFactory):
    def build_view(self) -> FormView:
        return FormView(
            name=f"{self.model.__name__}Form",
            model=self.model.__name__,
            fields=self.get_fields(),
        )


class ListViewFactory(BaseViewFactory):
    def build_view(self) -> ListView:
        return ListView(
            name=f"{self.model.__name__}List",
            model=self.model.__name__,
            default_form_id=f"{self.model.__name__}Form",
            fields=self.get_fields(),
        )
