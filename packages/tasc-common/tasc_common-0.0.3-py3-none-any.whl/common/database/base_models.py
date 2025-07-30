from typing import Optional, Union, List

from pydantic import BaseModel
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlmodel import SQLModel

from common.database.exceptions import DatabaseRowUnavailable
from common.database.session_manager import GlobalSessionManager as SessionManager
from common.database.utils import find_primary_key


class BaseSQLModel(SQLModel):
    @classmethod
    async def create(
        cls, model_create: Union["ModelCreate", BaseModel, None] = None, **kwargs
    ) -> "BaseSQLModel":
        if model_create is not None:
            create_dict = (
                model_create.create_dict()
                if isinstance(model_create, ModelCreate)
                else model_create.model_dump()
            )
            create_kwargs = {**create_dict, **kwargs}
        else:
            create_kwargs = dict(kwargs)
        # Validate the create_kwargs
        validated_kwargs = cls.model_validate(create_kwargs).model_dump()
        # Create the model
        model = await SessionManager.async_create(cls, **validated_kwargs)
        return model

    @classmethod
    async def get(
        cls,
        id: str = None,
        raise_error: bool = False,
        mode: str = "one",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> Union["BaseSQLModel", list["BaseSQLModel"], None]:
        try:
            kwargs = kwargs or {}

            if id is not None:
                pk_id = find_primary_key(cls)
                assert (
                    pk_id not in kwargs
                ), f"Primary key {pk_id} is already in kwargs, but id=... arg is specified."
                kwargs[pk_id] = id

            # Add offset and limit directly to kwargs
            if offset is not None:
                kwargs['offset'] = offset
            if limit is not None:
                kwargs['limit'] = limit

            return await SessionManager.async_get(cls, mode=mode, **kwargs)
        except (MultipleResultsFound, NoResultFound) as e:
            error_messages = {
                MultipleResultsFound: "Multiple records found for the given criteria.",
                NoResultFound: "No record found for the given criteria.",
            }
            if raise_error:
                raise DatabaseRowUnavailable(error_messages[type(e)])
            return None

    @classmethod
    async def get_or_create(cls, **kwargs) -> "BaseSQLModel":
        model = await cls.get(raise_error=False, **kwargs)
        if model is None:
            model = await cls.create(model_create=cls.model_validate(kwargs))  # noqa
        return model

    async def update(
        self, model_update: Union["ModelUpdate", BaseModel, dict, None] = None, **kwargs
    ) -> "BaseSQLModel":
        if model_update is not None:
            if isinstance(model_update, ModelUpdate):
                update_dict = model_update.update_dict()
            elif isinstance(model_update, BaseModel):
                update_dict = model_update.model_dump(exclude_unset=True)
            elif isinstance(model_update, dict):
                update_dict = model_update
            else:
                raise TypeError("model_update must be of type ModelUpdate, BaseModel, or dict")
            update_kwargs = {**update_dict, **kwargs}
        else:
            update_kwargs = dict(kwargs)

        model_update = self.model_validate(self.model_dump(), update=update_kwargs)
        model_data = model_update.model_dump(exclude_unset=True)
        self.sqlmodel_update(model_data)

        return await self.commit(do_refresh=True)

    async def delete(self) -> None:
        await SessionManager.async_delete(self)

    async def refresh(self) -> "BaseSQLModel":
        return await SessionManager.async_refresh(self)

    async def commit(self, do_refresh: bool = True) -> "BaseSQLModel":
        await SessionManager.async_add_and_commit(self)
        if do_refresh:
            await self.refresh()
        return self

    @classmethod
    async def count(cls, **kwargs) -> int:
        return await SessionManager.async_count(cls, **kwargs)

    @classmethod
    async def sort(cls, offset: Optional[int] = None, **kwargs) -> List["BaseSQLModel"]:
        if offset is not None:
            kwargs['offset'] = offset
        return await SessionManager.async_sort(cls, **kwargs)

    @classmethod
    async def simple_sort(
        cls,
        *,
        field: str,
        descending: bool = True,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List["BaseSQLModel"]:
        """Simple sorting interface for common use cases.

        Args:
            field: Field name to sort by
            descending: Sort in descending order if True, ascending if False
            offset: Number of items to skip
            limit: Maximum number of items to return
            **kwargs: Additional filter parameters

        Example:
            # Sort by creation date, newest first
            items = await Model.simple_sort(
                field="created_at",
                descending=True,
                limit=10,
                status="active"  # additional filter
            )
        """
        sort_order = SessionManager.descending() if descending else SessionManager.ascending()
        if limit is not None:
            sort_order.limit = limit

        return await cls.sort(
            offset=offset,
            **kwargs,
            **{field: sort_order}
        )


class ModelRead(BaseSQLModel):
    pass


class ModelCreate(BaseSQLModel):
    def create_dict(self) -> dict:
        return self.model_dump()


class ModelUpdate(BaseSQLModel):
    def update_dict(self):
        return self.model_dump(exclude_unset=True)
