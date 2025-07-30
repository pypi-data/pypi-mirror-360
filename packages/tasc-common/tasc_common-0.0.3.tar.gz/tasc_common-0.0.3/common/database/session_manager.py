import asyncio
import inspect
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from typing import Any, Optional, Union, List, Literal

from loguru import logger

from sqlalchemy import (
    Engine,
    Executable,
    and_,
    or_,
    create_engine,
    func,
    select,
    String,
    bindparam,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlmodel import Session, SQLModel, cast, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from common.database.utils import delete_object_with_dependencies


def session_manager_factory(echo: bool = True):
    class SessionManager:
        DB_URL = None
        ASYNC_ENGINE = None
        SYNC_ENGINE = None
        ASYNC_SESSION_FACTORY = None
        SYNC_SESSION_FACTORY = None
        # Context vars ensure that the session is not shared between asyncio tasks (or fastapi requests),
        # like lord tiangolo intended
        ASYNC_SESSION_OBJECT = ContextVar("ASYNC_SESSION_OBJECT", default=None)
        SYNC_SESSION_OBJECT = ContextVar("SYNC_SESSION_OBJECT", default=None)

        class Predicate:
            def predicate(self, x):
                raise NotImplementedError

        @dataclass
        class gt(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x > self.value

        @dataclass
        class ge(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x >= self.value

        @dataclass
        class lt(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x < self.value

        @dataclass
        class le(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x <= self.value

        @dataclass
        class ne(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x != self.value

        @dataclass
        class like(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x.like(self.value)

        @dataclass
        class ilike(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x.ilike(self.value)

        @dataclass
        class regex(Predicate):  # noqa
            value: Union[str, List[str]]
            case_sensitive: bool = True
            pattern_in_column: bool = False
            match_mode: Literal["any", "all"] = (
                "any"  # Only relevant when value is a list
            )

            def predicate(self, x):
                operator = "~" if self.case_sensitive else "~*"

                # Handle single string case
                if isinstance(self.value, str):
                    if self.pattern_in_column:
                        return bindparam(None, self.value).op(operator)(x)
                    else:
                        return x.op(operator)(self.value)

                # Handle list case
                if self.pattern_in_column:
                    # When patterns are in column, we need to check if ANY/ALL of our values match the pattern
                    values = self.value
                    if self.match_mode == "any":
                        return or_(
                            *[bindparam(None, v).op(operator)(x) for v in values]
                        )
                    else:  # all
                        return and_(
                            *[bindparam(None, v).op(operator)(x) for v in values]
                        )
                else:
                    # When we provide patterns, we can use PostgreSQL's ANY/ALL
                    return x.op(operator)(
                        func.any(self.value)
                        if self.match_mode == "any"
                        else func.all(self.value)
                    )

        @dataclass
        class in_(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x.in_(self.value)

        @dataclass
        class notin_(Predicate):  # noqa
            value: Any

            def predicate(self, x):
                return x.notin_(self.value)

        @dataclass
        class full_text_search(Predicate):  # noqa
            value: Any
            jsonb_key: Optional[str] = None
            web_search_mode: bool = False
            language: str = "english"

            def build_tsquery(self):
                if self.web_search_mode:
                    return func.websearch_to_tsquery(self.language, self.value)
                else:
                    return func.plainto_tsquery(self.language, self.value)

            def build_tsvector(self, x):
                if self.jsonb_key is None:
                    target = x
                elif self.jsonb_key == "*":
                    # Special case where we're searching the entire jsonb object
                    target = func.jsonb_to_tsvector(self.language, x, '["all"]')
                else:
                    target = func.jsonb_extract_path_text(x, *self.jsonb_key.split("."))
                if self.jsonb_key == "*":
                    # Target is already a tsvector
                    tsvector = target
                else:
                    # Coalesce required to handle None values, and cast to handle jsonb dicts.
                    tsvector = func.to_tsvector(
                        self.language, cast(func.coalesce(target, ""), String)
                    )
                return tsvector

            def predicate(self, x):
                tsquery = self.build_tsquery()
                tsvector = self.build_tsvector(x)
                # Return the predicate
                return tsvector.op("@@")(tsquery)

        @classmethod
        def build_predicate(cls, x: Any, y: Any):
            if isinstance(y, cls.Predicate):
                return y.predicate(x)
            else:
                return x == y

        @classmethod
        def get_model_attr(cls, model, k):
            return getattr(model, k)

        class Stmt:
            def build(self, model, **kwargs):
                raise NotImplementedError

        class get_stmt(Stmt):  # noqa
            @staticmethod
            def build(
                model,
                join_models: Optional[list] = None,
                custom_predicates: Optional[list] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = None,
                **kwargs,
            ):
                stmt = select(model)
                predicates = []
                if join_models is not None:
                    for join_model in join_models:
                        # Build the join statement
                        if isinstance(join_model, (list, tuple)):
                            _join_model = join_model[0]
                            join_condition = join_model[1]
                            stmt = stmt.join(_join_model, join_condition)
                            join_model = _join_model
                        else:
                            stmt = stmt.join(join_model)
                        # Read the predicates corresponding to the join model
                        kwarg_key = f"{join_model.__tablename__}__"
                        join_predicates = [
                            SessionManager.build_predicate(
                                SessionManager.get_model_attr(
                                    join_model, k.replace(kwarg_key, "")
                                ),
                                v,
                            )
                            for k, v in kwargs.items()
                            if k.startswith(kwarg_key)
                        ]
                        predicates = predicates + join_predicates
                        # Remove the join model keys from the kwargs
                        kwargs = {
                            k: v
                            for k, v in kwargs.items()
                            if not k.startswith(kwarg_key)
                        }
                # Build the base predicates
                predicates = predicates + [
                    SessionManager.build_predicate(
                        SessionManager.get_model_attr(model, k), v
                    )
                    for k, v in kwargs.items()
                ]
                if custom_predicates is not None:
                    predicates = predicates + custom_predicates
                stmt = stmt.where(and_(*predicates))
                # Add pagination
                if offset is not None:
                    stmt = stmt.offset(offset)
                if limit is not None:
                    stmt = stmt.limit(limit)
                return stmt

        class count_stmt(Stmt):  # noqa
            @staticmethod
            def build(model, **kwargs):
                stmt = (
                    select(func.count())
                    .where(
                        and_(
                            *[
                                SessionManager.build_predicate(
                                    SessionManager.get_model_attr(model, k), v
                                )
                                for k, v in kwargs.items()
                            ]
                        )
                    )
                    .select_from(model)
                )
                return stmt

        @dataclass
        class rank_stmt(Stmt):  # noqa
            top_k: int = 100
            rank_by: Optional[str] = None
            filter_non_matches: bool = True

            def build(self, model, **kwargs):
                # First, we select everything like in get
                predicates = [
                    SessionManager.build_predicate(
                        SessionManager.get_model_attr(model, k), v
                    )
                    for k, v in kwargs.items()
                ]
                subquery = (
                    select(model).where(and_(*predicates)).limit(self.top_k).subquery()
                )

                # Now comes the fun part.
                # We allow for multiple search predicates. But if this is the case,
                # rank_by must be specified.
                if self.rank_by is None:
                    # Find the search predicates
                    search_predicate_keys = [
                        k
                        for k, v in kwargs.items()
                        if isinstance(v, SessionManager.full_text_search)
                    ]
                    if len(search_predicate_keys) == 0:
                        raise ValueError("No search predicates found.")
                    elif len(search_predicate_keys) > 1:
                        raise ValueError(
                            "Multiple search predicates found for ranking."
                        )
                    else:
                        rank_by = search_predicate_keys[0]
                else:
                    rank_by = self.rank_by
                search_predicate = kwargs[rank_by]
                if not isinstance(search_predicate, SessionManager.full_text_search):
                    raise ValueError("Ranking requires a full text search predicate.")

                # Use the predicate to extract the tsvector and tsquery
                tsquery = search_predicate.build_tsquery()
                tsvector = search_predicate.build_tsvector(
                    SessionManager.get_model_attr(model, rank_by)
                )

                subquery_alias = aliased(model, subquery)

                if self.filter_non_matches:
                    # Build the rank expression
                    stmt = (
                        select(model, func.ts_rank(tsvector, tsquery).label("rank"))
                        .join(
                            subquery_alias,
                            *(
                                SessionManager.get_model_attr(model, c)
                                == SessionManager.get_model_attr(subquery_alias, c)
                                for c in model.__table__.primary_key.columns.keys()
                            ),
                        )
                        .where(
                            tsvector.op("@@")(tsquery)
                        )  # Add this line to filter matching documents
                        .order_by(desc("rank"))
                    )
                else:
                    stmt = (
                        select(model, func.ts_rank(tsvector, tsquery).label("rank"))
                        .join(
                            subquery_alias,
                            *(
                                SessionManager.get_model_attr(model, c)
                                == SessionManager.get_model_attr(subquery_alias, c)
                                for c in model.__table__.primary_key.columns.keys()
                            ),
                        )
                        .order_by(desc("rank"))
                    )
                return stmt

        class SortOrder:
            def __init__(self, limit: Optional[int] = None):
                self.limit = limit

            def get_fn(self):
                raise NotImplementedError

        class descending(SortOrder):  # noqa
            def get_fn(self):
                return desc

        class ascending(SortOrder):  # noqa
            def get_fn(self):
                return asc

        class sort_stmt(Stmt):
            def build(self, model, offset: Optional[int] = None, **kwargs):
                predicates = [
                    SessionManager.build_predicate(
                        SessionManager.get_model_attr(model, k), v
                    )
                    for k, v in kwargs.items()
                    if not isinstance(v, SessionManager.SortOrder)
                ]
                sort_orders = [
                    (v.get_fn()(SessionManager.get_model_attr(model, k)), v.limit)
                    for k, v in kwargs.items()
                    if isinstance(v, SessionManager.SortOrder)
                ]

                stmt = select(model)

                if predicates:
                    stmt = stmt.where(and_(*predicates))
                if sort_orders:
                    stmt = stmt.order_by(*[order for order, _ in sort_orders])

                # Apply offset before limit
                if offset is not None:
                    stmt = stmt.offset(offset)

                # Apply the minimum limit from all sort orders
                total_limit = None
                for _, limit in sort_orders:
                    if limit is not None:
                        total_limit = (
                            limit if total_limit is None else min(total_limit, limit)
                        )
                if total_limit is not None:
                    stmt = stmt.limit(total_limit)

                return stmt

        @classmethod
        def get_async_engine(cls) -> Engine:
            if cls.ASYNC_ENGINE is None:
                cls.ASYNC_ENGINE = create_async_engine(
                    cls.DB_URL,
                    echo=echo,
                    future=True,
                    pool_size=20,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    pool_pre_ping=True,
                )
            return cls.ASYNC_ENGINE

        @classmethod
        def get_sync_engine(cls) -> Engine:
            if cls.SYNC_ENGINE is None:
                cls.SYNC_ENGINE = create_engine(
                    cls.DB_URL,
                    echo=echo,
                    future=True,
                    pool_size=20,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    pool_pre_ping=True,
                )
            return cls.SYNC_ENGINE

        @classmethod
        def make_async_session(cls) -> AsyncSession:
            if cls.ASYNC_SESSION_FACTORY is None:
                cls.ASYNC_SESSION_FACTORY = sessionmaker(
                    cls.get_async_engine(), class_=AsyncSession, expire_on_commit=False
                )
            return cls.ASYNC_SESSION_FACTORY()  # noqa

        @classmethod
        def make_sync_session(cls) -> Session:
            if cls.SYNC_SESSION_FACTORY is None:
                cls.SYNC_SESSION_FACTORY = sessionmaker(
                    cls.get_sync_engine(), class_=Session, expire_on_commit=False
                )
            return cls.SYNC_SESSION_FACTORY()

        @classmethod
        @asynccontextmanager
        async def using_async_session(cls):
            async with cls.make_async_session() as session:
                token = cls.ASYNC_SESSION_OBJECT.set(session)  # noqa
                yield session
                cls.ASYNC_SESSION_OBJECT.reset(token)

        @classmethod
        @contextmanager
        def using_sync_session(cls):
            session = cls.make_sync_session()
            token = cls.SYNC_SESSION_OBJECT.set(session)  # noqa
            try:
                yield session
            finally:
                cls.SYNC_SESSION_OBJECT.reset(token)
                session.close()

        @classmethod
        def get_async_session_object(cls, ensure_exists: bool = True) -> AsyncSession:
            if ensure_exists and cls.ASYNC_SESSION_OBJECT.get() is None:
                raise ValueError(
                    "Async session object not found. Use the 'using_async_session' context manager."
                )
            return cls.ASYNC_SESSION_OBJECT.get()  # noqa

        @classmethod
        def get_sync_session_object(cls, ensure_exists: bool = True) -> Session:
            if ensure_exists and cls.SYNC_SESSION_OBJECT.get() is None:
                raise ValueError(
                    "Sync session object not found. Use the 'using_sync_session' context manager."
                )
            return cls.SYNC_SESSION_OBJECT.get()  # noqa

        @classmethod
        def get_session_object(
            cls,
            ensure_exists: bool = True,
            ensure_async: bool = False,
            ensure_sync: bool = False,
            full_return: bool = False,
        ) -> Session | AsyncSession | dict[str, Any]:
            if cls.get_async_session_object(ensure_exists=False) is not None:
                assert (
                    cls.get_sync_session_object(ensure_exists=False) is None
                ), "Both async and sync session objects found."
                assert (
                    not ensure_sync
                ), "Ensure sync is True but async session object found."
                retval = cls.get_async_session_object(ensure_exists=False)
                session_type = "async"
            elif cls.get_sync_session_object(ensure_exists=False) is not None:
                assert (
                    cls.get_async_session_object(ensure_exists=False) is None
                ), "Both async and sync session objects found."
                assert (
                    not ensure_async
                ), "Ensure async is True but sync session object found."
                retval = cls.get_sync_session_object(ensure_exists=False)
                session_type = "sync"
            else:
                retval = None
                session_type = None
            if retval is None and ensure_exists:
                raise ValueError("Session object not found.")
            if full_return:
                return dict(session=retval, session_type=session_type)
            else:
                return retval

        @classmethod
        def with_async_session(cls, func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                async with cls.using_async_session():
                    return await func(*args, **kwargs)

            return wrapper

        @classmethod
        def with_sync_session(cls, func):
            @wraps(func)
            def wrapper_sync(*args, **kwargs):
                with cls.using_sync_session() as session:  # noqa
                    return func(*args, **kwargs)

            @wraps(func)
            async def wrapper_async(*args, **kwargs):
                with cls.using_sync_session() as session:  # noqa
                    return await func(*args, **kwargs)

            if inspect.iscoroutinefunction(func):
                return wrapper_async
            else:
                return wrapper_sync

        @classmethod
        def add_to_session(cls, *objects, ensure_exists: bool = True):
            # Get the session
            session = cls.get_session_object(ensure_exists=ensure_exists)
            if session is not None:
                # Add the objects to the session
                for obj in objects:
                    session.add(obj)

        @classmethod
        async def async_commit_session(
            cls,
            ensure_exists: bool = True,
            ensure_async: bool = False,
            ensure_sync: bool = False,
            run_in_thread: bool = True,
            do_commit: bool = True,
        ):
            if not do_commit:
                return
            # Get the session
            session_info = cls.get_session_object(
                ensure_exists=ensure_exists,
                ensure_sync=ensure_sync,
                ensure_async=ensure_async,
                full_return=True,
            )
            if session_info["session_type"] == "async":
                await session_info["session"].commit()
            elif session_info["session_type"] == "sync":
                if run_in_thread:
                    await asyncio.to_thread(session_info["session"].commit)
                else:
                    session_info["session"].commit()
            elif ensure_exists:
                raise ValueError("Session object not found.")

        @classmethod
        def commit_session(cls, ensure_exists: bool = True, do_commit: bool = True):
            if not do_commit:
                return
            session_info = cls.get_session_object(
                ensure_exists=ensure_exists, full_return=True
            )
            if session_info["session_type"] == "sync":
                session_info["session"].commit()
            elif session_info["session_type"] == "async":
                raise ValueError("Use 'async_commit_session' for async sessions.")
            elif ensure_exists:
                raise ValueError("Session object not found.")

        @classmethod
        async def async_exec(cls, stmt: Executable, run_in_thread: bool = True):
            session_info = cls.get_session_object(ensure_exists=True, full_return=True)
            if session_info["session_type"] == "sync":
                if run_in_thread:
                    result = await asyncio.to_thread(session_info["session"].exec, stmt)
                else:
                    result = session_info["session"].exec(stmt)
            elif session_info["session_type"] == "async":
                result = await session_info["session"].exec(stmt)
            else:
                raise ValueError(
                    f"Session type not valid: {session_info['session_type']}"
                )
            return result

        @classmethod
        def exec(cls, stmt: Executable):
            session_info = cls.get_session_object(ensure_exists=True, full_return=True)
            if session_info["session_type"] == "sync":
                result = session_info["session"].exec(stmt)
            elif session_info["session_type"] == "async":
                raise ValueError("Use 'async_exec' for async sessions.")
            else:
                raise ValueError(
                    f"Session type not valid: {session_info['session_type']}"
                )
            return result

        @staticmethod
        def get_from_result(result, mode: str, scalars: bool = True):
            if scalars:
                result = result.scalars()
            if mode == "all":
                return result.all()
            elif mode == "one":
                return result.one()
            elif mode == "first":
                return result.first()
            else:
                raise ValueError("Invalid mode, must be 'all', 'one', or 'first'.")

        @classmethod
        async def async_get(
            cls,
            model,
            mode: str = "all",
            stmt: Optional[Stmt] = None,
            get_scalars: bool = True,
            run_in_thread: bool = True,
            **kwargs,
        ):
            if stmt is None:
                stmt = cls.get_stmt()
            stmt_ = stmt.build(model, **kwargs)
            result = await cls.async_exec(stmt_, run_in_thread=run_in_thread)
            return cls.get_from_result(result, mode, scalars=get_scalars)

        @classmethod
        def get(
            cls,
            model,
            mode: str = "all",
            stmt: Optional[Stmt] = None,
            get_scalars: bool = True,
            **kwargs,
        ):
            if stmt is None:
                stmt = cls.get_stmt()
            stmt_ = stmt.build(model, **kwargs)
            result = cls.exec(stmt_)
            return cls.get_from_result(result, mode, scalars=get_scalars)

        @classmethod
        async def async_count(cls, model, **kwargs):
            stmt_ = cls.count_stmt().build(model, **kwargs)
            result = await cls.async_exec(stmt_)
            return result.scalar()

        @classmethod
        def count(cls, model, **kwargs):
            stmt_ = cls.count_stmt().build(model, **kwargs)
            return cls.exec(stmt_).scalar()

        @classmethod
        async def async_sort(
            cls, model, get_scalars: bool = True, run_in_thread: bool = True, **kwargs
        ):
            stmt_ = cls.sort_stmt().build(model, **kwargs)
            result = await cls.async_exec(stmt_, run_in_thread=run_in_thread)
            return cls.get_from_result(result, mode="all", scalars=get_scalars)

        @classmethod
        def sort(cls, model, get_scalars: bool = True, **kwargs):
            stmt_ = cls.sort_stmt().build(model, **kwargs)
            result = cls.exec(stmt_)
            return cls.get_from_result(result, mode="all", scalars=get_scalars)

        @classmethod
        async def async_get_one(cls, model, run_in_thread: bool = True, **kwargs):
            return await cls.async_get(
                model,
                mode="one",
                get_scalars=True,
                run_in_thread=run_in_thread,
                **kwargs,
            )

        @classmethod
        def get_one(cls, model, **kwargs):
            return cls.get(model, mode="one", get_scalars=True, **kwargs)

        @classmethod
        async def async_refresh(
            cls,
            *objects,
            run_in_thread: bool = True,
        ):
            session_info = cls.get_session_object(ensure_exists=True, full_return=True)
            for obj in objects:
                if session_info["session_type"] == "sync":
                    if run_in_thread:
                        await asyncio.to_thread(session_info["session"].refresh, obj)
                    else:
                        session_info["session"].refresh(obj)
                elif session_info["session_type"] == "async":
                    await session_info["session"].refresh(obj)
                else:
                    raise ValueError(
                        f"Session type not valid: {session_info['session_type']}"
                    )
            if len(objects) == 1:
                return objects[0]
            else:
                return objects

        @classmethod
        def refresh(cls, *objects):
            session_info = cls.get_session_object(ensure_exists=True, full_return=True)
            for obj in objects:
                if session_info["session_type"] == "sync":
                    session_info["session"].refresh(obj)
                elif session_info["session_type"] == "async":
                    raise ValueError("Use 'async_refresh' for async sessions.")
                else:
                    raise ValueError(
                        f"Session type not valid: {session_info['session_type']}"
                    )
            if len(objects) == 1:
                return objects[0]
            else:
                return objects

        @classmethod
        def delete(cls, *objects):
            # TODO: Support for async engine when we need it
            session = cls.get_session_object(ensure_exists=True, ensure_sync=True)
            for obj in objects:
                session.delete(obj)
            cls.commit_session()

        @classmethod
        async def async_delete(cls, *objects):
            # TODO: Support for async engine when we need it
            session = cls.get_session_object(ensure_exists=True, ensure_sync=True)
            for obj in objects:
                session.delete(obj)
            await cls.async_commit_session()

        @classmethod
        def create(
            cls,
            constructor: Callable[..., SQLModel],
            do_add: bool = True,
            do_commit: bool = True,
            do_refresh: bool = True,
            **kwargs,
        ) -> SQLModel:
            obj = constructor(**kwargs)
            if do_add:
                cls.add_to_session(obj)
            if do_add and do_commit:
                cls.commit_session()
            if do_add and do_commit and do_refresh:
                cls.refresh(obj)
            return obj

        @classmethod
        async def async_create(
            cls,
            constructor: Callable[..., SQLModel],
            do_add: bool = True,
            do_commit: bool = True,
            do_refresh: bool = True,
            **kwargs,
        ) -> SQLModel:
            obj = constructor(**kwargs)
            if do_add:
                cls.add_to_session(obj)
            if do_add and do_commit:
                await cls.async_commit_session()
            if do_add and do_commit and do_refresh:
                await cls.async_refresh(obj)
            return obj

        @classmethod
        def add_and_commit(cls, *objects, do_refresh: bool = True):
            cls.add_to_session(*objects)
            cls.commit_session()
            if do_refresh:
                cls.refresh(*objects)
            if len(objects) == 1:
                return objects[0]
            else:
                return objects

        @classmethod
        async def async_add_and_commit(cls, *objects, do_refresh: bool = True):
            cls.add_to_session(*objects)
            await cls.async_commit_session()
            if do_refresh:
                await cls.async_refresh(*objects)
            if len(objects) == 1:
                return objects[0]
            else:
                return objects

        @classmethod
        def delete_with_dependencies(cls, obj: SQLModel):
            session = cls.get_session_object(ensure_sync=True)
            delete_object_with_dependencies(session, obj)
            return obj

    return SessionManager


GlobalSessionManager = session_manager_factory(echo=False)


async def get_one(model, **kwargs):
    return await GlobalSessionManager.async_get(model, mode="one", **kwargs)
