from fastapi import FastAPI


class FpAdmin(FastAPI):
    admin_path: str = "/admin"

    def setup(self) -> None:
        from fp_admin.api import api_router
        from fp_admin.core.loader import load_modules

        load_modules(self)
        self.include_router(api_router, prefix=self.admin_path)
