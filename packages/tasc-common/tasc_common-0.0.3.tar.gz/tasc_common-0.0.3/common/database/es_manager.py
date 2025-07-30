import uuid
from enum import Enum
from typing import TYPE_CHECKING, Type, Union
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
from pydantic.fields import FieldInfo

if TYPE_CHECKING:
    from common.database.search_model import BaseSearchModel


def es_index_factory():
    class ESManager:
        ES_URL: str = None
        ES_CLIENT: AsyncElasticsearch = None

        @classmethod
        def get_es_client(cls) -> AsyncElasticsearch:
            if cls.ES_CLIENT is None:
                cls.ES_CLIENT = AsyncElasticsearch(cls.ES_URL)
            return cls.ES_CLIENT

        class ESIndex:
            def __init__(self, index_name: str, mappings: dict = None):
                self.index_name = index_name
                self.mappings = {} if mappings is None else mappings

            async def create(self):
                client = ESManager.get_es_client()

                # Check if index already exists
                if await client.indices.exists(index=self.index_name):
                    return

                try:
                    await client.indices.create(
                        index=self.index_name,
                        body=self.mappings,
                    )
                    return self
                except Exception as e:
                    # Re-raise with more context
                    raise Exception(
                        f"Failed to create index {self.index_name}: {str(e)}"
                    ) from e

        INDEX_REGISTRY: dict[str, ESIndex] = {}

        @classmethod
        async def get_or_create_index(
            cls, model_class: Type["BaseSearchModel"]
        ) -> "ESIndex":
            index_name = model_class.get_index_name()
            if index_name in cls.INDEX_REGISTRY:
                return cls.INDEX_REGISTRY[index_name]
            es_index = cls.ESIndex(
                index_name=index_name, mappings=cls.build_mappings(model_class)
            )
            await es_index.create()
            cls.INDEX_REGISTRY[index_name] = es_index
            return es_index

        @classmethod
        def build_mappings(cls, model_class: Type[BaseModel]) -> dict:
            return {"mappings": cls.build_properties(model_class)}

        @classmethod
        def build_properties(cls, model_class: Type[BaseModel]) -> dict:
            simple_elastic_py_types = {
                bool: "boolean",
                int: "integer",
                float: "float",
                str: "text",
                bytes: "binary",
                dict: "object",
            }

            def get_simple_es_type(_field: FieldInfo, _field_name: str) -> str:
                annotation = _field.annotation
                if annotation is None:
                    raise ValueError(f"Missing annotation for field {_field_name}")

                # Handle Optional/Union types
                if (
                    hasattr(annotation, "__origin__")
                    and getattr(annotation, "__origin__") is Union
                ):
                    types = getattr(annotation, "__args__")
                    # Filter out None/NoneType
                    non_none_types = [t for t in types if t not in (None, type(None))]
                    if len(non_none_types) == 1:
                        # If only one non-None type, use that
                        annotation = non_none_types[0]
                    else:
                        raise ValueError(
                            f"Complex union types not supported for field {_field_name}"
                        )

                if annotation in simple_elastic_py_types:
                    return simple_elastic_py_types[annotation]  # noqa
                else:
                    raise ValueError(
                        f"Unsupported type {annotation} for field {_field_name}"
                    )

            properties = {}
            for field_name, field in model_class.model_fields.items():
                if isinstance(field.json_schema_extra, dict):
                    es_ignore = field.json_schema_extra.get("x-es-ignore", False)
                else:
                    es_ignore = False

                if es_ignore:
                    continue

                es_properties = dict(
                    (field.json_schema_extra or {}).get("x-es-properties", {})
                )

                # Check if type is already specified in es_properties
                if "type" in es_properties:
                    properties[field_name] = es_properties
                    continue

                # Handle nested SearchModel types
                if (
                    hasattr(field.annotation, "__origin__")
                    and field.annotation.__origin__ is list
                ):
                    # Handle List[SearchModel] type
                    inner_type = field.annotation.__args__[0]
                    if issubclass(inner_type, BaseModel):
                        es_properties.update(
                            {
                                "type": "nested",
                                "properties": cls.build_properties(inner_type)[
                                    "properties"
                                ],
                            }
                        )
                elif issubclass(field.annotation, BaseModel):
                    # Handle nested SearchModel type
                    es_properties.update(
                        {
                            "type": "nested",
                            "properties": cls.build_properties(field.annotation)[
                                "properties"
                            ],
                        }
                    )
                elif "type" not in es_properties:
                    es_properties["type"] = get_simple_es_type(field, field_name)

                properties[field_name] = es_properties

            return {"properties": properties}

        class SearchResult:
            def __init__(
                self,
                model: "BaseSearchModel",
                score: float,
                total: int,
                response_uuid: str,
            ):
                self.model = model
                self.score = score
                self.total = total
                self.response_uuid = response_uuid

        @classmethod
        async def search(
            cls,
            model_class: Type["BaseSearchModel"],
            query: dict,
            *,
            size: int = 10,
            from_: int = 0,
            **kwargs,
        ) -> list[SearchResult]:
            """
            Execute a search query and return parsed results.

            Args:
                model_class: The SearchModel class to search
                query: Elasticsearch query dict
                size: Number of results to return
                from_: Starting offset
                **kwargs: Additional parameters to pass to search API
            """
            index = await cls.get_or_create_index(model_class)
            client = cls.get_es_client()

            response = await client.search(
                index=index.index_name, body=query, size=size, from_=from_, **kwargs
            )
            response_uuid = uuid.uuid4().hex

            hits = response["hits"]
            total = hits["total"]["value"]
            results = []
            for hit in hits["hits"]:
                data = hit["_source"]
                data["id"] = hit["_id"]  # Use ES _id as model id
                results.append(
                    cls.SearchResult(
                        model=model_class(**data),
                        score=hit["_score"],
                        total=total,
                        response_uuid=response_uuid,
                    )
                )

            return results

        @classmethod
        async def multi_search(
            cls, model_class: Type["BaseSearchModel"], queries: list[dict], **kwargs
        ) -> list[list[SearchResult]]:
            """
            Execute multiple searches in one request.

            Args:
                model_class: The SearchModel class to search
                queries: List of Elasticsearch query dicts
                **kwargs: Additional parameters to pass to msearch API

            Returns:
                list[list[SearchResult]]: List of SearchResult lists, one for each query
            """
            index = await cls.get_or_create_index(model_class)
            client = cls.get_es_client()

            # Build msearch body
            body = []
            for query in queries:
                body.extend([{"index": index.index_name}, query])

            response = await client.msearch(body=body, **kwargs)

            results = []
            for response_item in response["responses"]:
                hits = response_item["hits"]
                total = hits["total"]["value"]
                response_uuid = uuid.uuid4().hex
                items = []
                for hit in hits["hits"]:
                    data = hit["_source"]
                    data["id"] = hit["_id"]  # Use ES _id as model id
                    items.append(
                        cls.SearchResult(
                            model=model_class(**data),
                            score=hit["_score"],
                            total=total,
                            response_uuid=response_uuid,
                        )
                    )
                results.append(items)

            return results

        @classmethod
        async def index(cls, model: "BaseSearchModel", **kwargs) -> None:
            """Index a document, using model.id as the document _id"""
            index = await cls.get_or_create_index(model.__class__)
            client = cls.get_es_client()

            await client.index(
                index=index.index_name,
                id=model.id,
                document=model.model_dump(exclude={"id"}),
                **kwargs,
            )

        @classmethod
        async def bulk_index(
            cls, models: list["BaseSearchModel"], *, refresh: bool = False, **kwargs
        ) -> dict:
            """
            Bulk index multiple documents.

            Args:
                models: List of models to index
                refresh: Whether to refresh the index immediately
                **kwargs: Additional parameters to pass to bulk API

            Returns:
                dict: Elasticsearch bulk operation response
            """
            if not models:
                return {}

            # All models must be of the same type
            model_class = models[0].__class__
            if not all(isinstance(m, model_class) for m in models):
                raise ValueError("All models must be of the same type")

            index = await cls.get_or_create_index(model_class)
            client = cls.get_es_client()

            # Build bulk operation body
            operations = []
            for model in models:
                operations.extend(
                    [
                        {"index": {"_index": index.index_name, "_id": model.id}},
                        model.model_dump(exclude={"id"}),
                    ]
                )

            return await client.bulk(operations=operations, refresh=refresh, **kwargs)

    return ESManager


GlobalESManager = es_index_factory()
