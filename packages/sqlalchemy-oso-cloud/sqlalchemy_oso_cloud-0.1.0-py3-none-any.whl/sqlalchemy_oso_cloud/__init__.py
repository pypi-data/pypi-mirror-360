"""
[SQLAlchemy](https://www.sqlalchemy.org/) extension for
[Local Authorization with Oso Cloud](https://www.osohq.com/docs/authorization-data/local-authorization).

This library provides first-class SQLAlchemy support for Oso Cloud,
allowing you to filter queries against your database based on a user's access
to the data.

The main features are:
- Automatic Local Authorization configuration from your ORM models
  via utilities provided in the `.orm` module.
- Extensions to SQLAlchemy's `Select` and `Query` classes to provide
  an `.authorized_for(actor, action)` method for filtering results.

See the [README](https://github.com/osohq/sqlalchemy-oso-cloud) for more information.
"""
from . import orm
from .session import Session
from .query import Query
from .oso import init, get_oso
from .select_impl import Select, select
from .auth import authorized, _apply_authorization_options

__all__ = ["orm", "Session", "Query", "init", "get_oso", "Select", "select", "authorized", "_apply_authorization_options"]
