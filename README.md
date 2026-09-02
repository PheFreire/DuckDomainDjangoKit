# 🦆 DuckDomainDjangoKit (`dddk`)

**DuckDomainDjangoKit** is a small set of domain and repository-layer
building blocks for Django backends: typed DTOs, a repository interface,
structured error handling, a FK/M2M/HasMany relation loader, and an
environment-config abstraction. It's the extracted, reusable core shared
across multiple Django projects.

It pairs naturally with [DuckDI](https://pypi.org/project/duckdi/) for
dependency injection.

---

## 📦 Installation

With [Poetry](https://python-poetry.org):

```bash
poetry add duck-domain-django-kit
```

Or using pip:

```bash
pip install duck-domain-django-kit
```

## 🚀 What's inside

- **DTOs** — `BaseDto`, `RequestDto`, `CreateDto`, `UpdateDto`, `WhereDto`,
  plus the `Null` / `NullOr[T]` sentinel types for distinguishing "not sent"
  from `None`.
- **Repository pattern** — `IRepository` interface and `QueryResponse` for
  ORM-agnostic data access.
- **Django repository/admin helpers** — `SoftDeleteModel`,
  `SoftDeleteDjangoRepository`, `SoftDeleteAdmin`, `get_if_active` (lazily
  imported, only touch Django when actually used).
- **Relation loader** — `RelationLoader` with `FkRelationConfig`,
  `HasManyRelationConfig`, `M2MRelationConfig`,
  `M2MWithPivotRelationConfig` to declaratively hydrate related data.
- **Errors** — `AppError`, a structured application error base class.
- **Envs** — `IEnvs` interface and an adapter exposing the database
  connection settings from the `DATABASE_URL` environment variable.

```python
from dddk import (
    BaseDto,
    IRepository,
    WhereDto,
    QueryResponse,
    AppError,
)
```

## 🧑‍💻 Development

```bash
make help
```

- `make format` — pyupgrade, autoflake, isort, black
- `make check` — bandit, black, isort, flake8, mypy
- `make test` — pytest
- `make pub` — bump patch version, build and publish to PyPI
