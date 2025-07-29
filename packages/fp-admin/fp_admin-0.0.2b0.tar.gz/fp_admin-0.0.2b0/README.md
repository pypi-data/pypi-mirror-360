# fastapi-admin

Install all dependencies
```bash
uv sync --all-extras --dev
````



Install the git hook scripts

```bash
pre-commit install
```

RUN pre-commit:

```bash
pre-commit run --all-files
```

Run Server:

```bash
python main.py
```

CLI:

Make migrations

```bash
python fp_admin/manage.py make-migrations -n create_tables
```

Run migrations

```bash
python fp_admin/manage.py migrate
```
