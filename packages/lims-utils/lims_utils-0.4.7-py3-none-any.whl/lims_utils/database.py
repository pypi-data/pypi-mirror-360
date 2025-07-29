import contextlib
from contextvars import ContextVar
from typing import Generator, Optional, Sequence, Tuple, TypeVar

from sqlalchemy import Row, Select, func, literal_column, select
from sqlalchemy.orm import Session, sessionmaker

from .models import Paged

_inner_session: ContextVar[Session | None] = ContextVar("_inner_session", default=None)

T = TypeVar("T")


class Database:
    """Database session provider helper class. All it does is check whether or not a session is set, and if not
    raise an exception."""

    @classmethod
    def set_session(cls, session):
        _inner_session.set(session)

    @property
    def session(self) -> Session:
        try:
            current_session = _inner_session.get()
            if current_session is None:
                raise AttributeError
            return current_session
        except (AttributeError, LookupError):
            raise Exception("Can't get session. Please call Database.set_session()")

    def fast_count(self, query: Select) -> int:
        return self.session.execute(
            query.with_only_columns(func.count(literal_column("1"))).order_by(None)
        ).scalar_one()

    def paginate(
        self,
        query: Select[Tuple[T]],
        limit: int,
        page: int,
        slow_count=True,
        precounted_total: Optional[int] = None,
        scalar=True,
    ):
        """Paginate a query before querying database

        Args:
            query: Original query
            limit: Number of items to return per page
            page: Page to access
            slow_count: Count number of total items in a slower, safer manner (useful with GROUP statements)
            precounted_total: Skip count, use this total instead
            scalar: Is query already scalar (use `execute` instead of `scalars` when executing)

        Returns
            Paged representation of query"""

        if precounted_total is not None:
            total = precounted_total
        elif slow_count:
            total = self.session.execute(
                select(func.count(literal_column("1"))).select_from(query.subquery())
            ).scalar_one()
        else:
            total = self.fast_count(query)

        data: Sequence[Row[Tuple[T]]] | Sequence[T] = []

        if total:
            if page < 0:
                page = (total // limit) + page

            new_query = query.limit(limit).offset((page) * limit)

            if scalar:
                data = self.session.execute(new_query).all()
            else:
                data = self.session.scalars(new_query).all()

        return Paged(items=data, total=total, limit=limit, page=page)


@contextlib.contextmanager
def get_session(session_maker: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Database session context manager. Can be used with `Database` and context vars, which is the default
    implementation, but works well on its own as a context manager or dependency.

    Args:
        session_maker: Session maker, returned by SQLAlchemy ORM's `sessionmaker` builder.
    """
    inner_db_session = session_maker()
    try:
        Database.set_session(inner_db_session)
        yield inner_db_session
    except Exception:
        inner_db_session.rollback()
        raise
    finally:
        Database.set_session(None)
        inner_db_session.close()
