import uuid
from enum import Enum
from typing import Any, ClassVar, Type, TypeVar, Generic, Optional, Literal

from pydantic import BaseModel
from pydantic.fields import FieldInfo, Field

from common.database.es_manager import GlobalESManager as ESManager
from common.utils import NoValue


def _parse_field(
    field: FieldInfo | NoValue | Any,
    default: Any = NoValue(),
    default_factory: Any = NoValue(),
) -> FieldInfo:
    """
    Parse field input into a FieldInfo object.

    Args:
        field: The field specification (FieldInfo, ..., or NoValue)
        default: Default value for the field
        default_factory: Callable that returns the default value

    Returns:
        FieldInfo: A properly configured field info object
    """
    # Can't specify both default and default_factory
    if not isinstance(default, NoValue) and not isinstance(default_factory, NoValue):
        raise ValueError("Cannot specify both default and default_factory")

    # If field is already a FieldInfo, just return it
    if isinstance(field, FieldInfo):
        assert isinstance(default, NoValue) and isinstance(
            default_factory, NoValue
        ), "Cannot specify default or default_factory with FieldInfo"
        return field

    # If field is Ellipsis (...), create new FieldInfo
    if field is ...:
        if isinstance(default, NoValue) and isinstance(default_factory, NoValue):
            return Field(...)
        if not isinstance(default, NoValue):
            return Field(default=default)
        return Field(default_factory=default_factory)

    # If field is NoValue, handle default/default_factory
    if isinstance(field, NoValue):
        if isinstance(default, NoValue) and isinstance(default_factory, NoValue):
            return Field()
        if not isinstance(default, NoValue):
            return Field(default=default)
        return Field(default_factory=default_factory)

    raise ValueError(f"Invalid field specification: {field}")


def SearchField(
    field: FieldInfo | NoValue | Any = NoValue(),
    *,
    default: Any = NoValue(),
    default_factory: Any = NoValue(),
    es_ignore: bool = False,
    es_type: str | None = None,
    es_dynamic: bool | str = None,
    es_null_value: str | None = None,
    es_analyzer: str | None = None,
    es_fields: dict | None = None,
    es_properties: dict | None = None,
) -> Any:
    json_schema_update = {}

    field = _parse_field(field=field, default=default, default_factory=default_factory)

    if es_ignore:
        json_schema_update["x-es-ignore"] = es_ignore
        assert es_type is None, "Cannot specify es_type when es_ignore is True"
        assert (
            es_properties is None
        ), "Cannot specify es_properties when es_ignore is True"

    es_properties = es_properties or {}
    if es_type is not None:
        es_properties["type"] = es_type

    if es_dynamic is not None:
        es_properties["dynamic"] = es_dynamic

    if es_null_value is not None:
        es_properties["null_value"] = es_null_value

    if es_analyzer is not None:
        if es_properties.get("type") is None:
            # Default to text if type not specified
            es_properties["type"] = "text"
        es_properties["analyzer"] = es_analyzer

    if es_fields is not None:
        es_properties["fields"] = es_fields

    if es_properties:
        json_schema_update["x-es-properties"] = es_properties

    if isinstance(field.json_schema_extra, dict):
        field.json_schema_extra.update(json_schema_update)
    else:
        assert (
            field.json_schema_extra is None
        ), f"Unexpected json_schema_extra: {field.json_schema_extra}"
        field.json_schema_extra = json_schema_update

    return field


def DenseVectorField(
    field: FieldInfo | NoValue | Any = NoValue(),
    *,
    default: Any = NoValue(),
    default_factory: Any = NoValue(),
    dims: int,
    index: bool = True,
    similarity: str = "cosine",
    m: int | None = None,
    ef_construction: int | None = None,
    es_properties: dict | None = None,
) -> Any:
    """
    Helper function to create dense vector fields with optional HNSW parameters.

    Args:
        field: The base field info
        default: Default value for the field
        default_factory: Callable that returns the default value
        dims: Vector dimensions (required)
        index: Whether to make the vector searchable
        similarity: Similarity metric ("cosine", "dot_product", or "l2_norm")
        m: HNSW graph parameter - maximum number of connections per node (default: 16)
        ef_construction: HNSW construction parameter - controls index build quality (default: 100)
        es_properties: Additional ES properties to merge
    """

    es_properties = es_properties or {}
    vector_props = {
        "type": "dense_vector",
        "dims": dims,
        "index": index,
        "similarity": similarity,
    }

    if index and (m is not None or ef_construction is not None):
        # Only add HNSW parameters if the vector is indexed
        vector_props["index_options"] = {
            "type": "hnsw",
            **({"m": m} if m is not None else {}),
            **(
                {"ef_construction": ef_construction}
                if ef_construction is not None
                else {}
            ),
        }

    es_properties.update(vector_props)
    return SearchField(
        field,
        default=default,
        default_factory=default_factory,
        es_properties=es_properties,
    )


def DictField(
    field: FieldInfo | NoValue | Any = NoValue(),
    *,
    default: Any = NoValue(),
    default_factory: Any = NoValue(),
    properties: dict | None = None,
    dynamic: bool | str = False,
) -> Any:
    """
    Helper function to create dictionary fields with explicit mappings.

    Args:
        field: The base field info
        default: Default value for the field
        default_factory: Callable that returns the default value
        properties: Nested field mappings
        dynamic: Whether to allow dynamic field
    """
    es_properties = {"type": "object", "dynamic": dynamic}
    if properties:
        es_properties["properties"] = properties

    return SearchField(
        field,
        default=default,
        default_factory=default_factory,
        es_properties=es_properties,
    )


class Sort(str, Enum):
    ASC = "asc"
    DESC = "desc"


T = TypeVar("T", bound="BaseSearchModel")


class QueryBuilder(Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.query = {"bool": {"must": [], "should": [], "must_not": [], "filter": []}}
        self.knn_queries = []
        self.size_value = 10
        self.from_value = 0
        self.sort_fields = []

    def knn(
        self,
        field: str,
        vector: list[float],
        k: int = 10,
        num_candidates: int = 100,
        **pre_filters,
    ) -> "QueryBuilder[T]":
        """Add KNN vector search to the query."""
        # Each knn query should be a separate top-level clause
        params = {
            "field": field,
            "query_vector": vector,
            "k": k,
            "num_candidates": num_candidates,
        }
        if pre_filters:
            params["filter"] = [
                {"term": {key: value}} for key, value in pre_filters.items()
            ]
        self.knn_queries.append(params)
        return self

    def must(self, **kwargs) -> "QueryBuilder[T]":
        """Field must match the given value(s)"""
        for field, value in kwargs.items():
            self.query["bool"]["must"].append({"match": {field: value}})
        return self

    def should(self, **kwargs) -> "QueryBuilder[T]":
        """Field should match any of the given values"""
        for field, value in kwargs.items():
            self.query["bool"]["should"].append({"match": {field: value}})
        return self

    def must_not(self, **kwargs) -> "QueryBuilder[T]":
        """Field must not match the given value(s)"""
        for field, value in kwargs.items():
            self.query["bool"]["must_not"].append({"match": {field: value}})
        return self

    def filter(self, **kwargs):
        """Field must match the given value(s) without scoring"""
        for field, value in kwargs.items():
            self.query["bool"]["filter"].append({"term": {field: value}})
        return self

    def filter_range(
        self, field: str, gt=None, gte=None, lt=None, lte=None
    ) -> "QueryBuilder[T]":
        """Add range filters"""
        range_params = {}
        if gt is not None:
            range_params["gt"] = gt
        if gte is not None:
            range_params["gte"] = gte
        if lt is not None:
            range_params["lt"] = lt
        if lte is not None:
            range_params["lte"] = lte

        if range_params:
            self.query["bool"]["filter"].append({"range": {field: range_params}})
        return self

    def sort(self, field: str, order: Sort = Sort.ASC) -> "QueryBuilder[T]":
        """Add sort criteria"""
        self.sort_fields.append({field: order})
        return self

    def size(self, size: int) -> "QueryBuilder[T]":
        """Set result size"""
        self.size_value = size
        return self

    def offset(self, offset: int) -> "QueryBuilder[T]":
        """Set starting offset"""
        self.from_value = offset
        return self

    def merge(self, other: "QueryBuilder") -> "QueryBuilder":
        """
        Merge another QueryBuilder's conditions into this one.

        Args:
            other: Another QueryBuilder instance to merge from

        Returns:
            self: Returns self for method chaining
        """
        if "bool" in other.query:
            if "bool" not in self.query:
                self.query["bool"] = {}
            for condition, values in other.query["bool"].items():
                if condition not in self.query["bool"]:
                    self.query["bool"][condition] = values.copy()
                else:
                    self.query["bool"][condition].extend(values)

        return self

    def build(self) -> dict:
        """Build the final query dict"""
        query_dict = {}

        if self.knn_queries:
            # KNN is a top-level parameter in ES 8.x
            knn_query = self.knn_queries[0]  # Currently only supporting one KNN query
            query_dict["knn"] = knn_query

            # If we have bool conditions, add them as a query filter
            if any(self.query["bool"].values()):
                query_dict["query"] = {"bool": self.query["bool"]}
        elif any(self.query["bool"].values()):
            # If we only have boolean conditions
            query_dict["query"] = {"bool": self.query["bool"]}

        if self.sort_fields:
            query_dict["sort"] = self.sort_fields

        return query_dict

    async def execute(self) -> list[ESManager.SearchResult]:
        """Execute the query and return results with scores and metadata"""
        query_dict = self.build()
        return await self.model_class.search_interface(
            query_dict, size=self.size_value, from_=self.from_value
        )


class BaseSearchModel(BaseModel):
    __es_index_name__: ClassVar[str | None] = None
    __es_index__: ClassVar[ESManager.ESIndex | None] = None

    id: str = SearchField(
        Field(default_factory=lambda: str(uuid.uuid4().hex)),
        es_ignore=True,  # Don't store in _source since we'll use ES _id
    )

    @classmethod
    def query(cls) -> QueryBuilder["BaseSearchModel"]:
        """Start building a query for this model"""
        return QueryBuilder(cls)

    @classmethod
    async def get_index(cls) -> ESManager.ESIndex:
        if cls.__es_index__ is None:
            # Build the index
            cls.__es_index__ = await ESManager.get_or_create_index(cls)
        return cls.__es_index__

    @classmethod
    def get_index_name(cls) -> str:
        if cls.__es_index_name__ is None:
            cls.__es_index_name__ = cls.__name__.lower()
        return cls.__es_index_name__

    @classmethod
    async def get(cls, id: str) -> Optional["BaseSearchModel"]:
        """
        Retrieve a document by its ID.

        Args:
            id: Document ID

        Returns:
            BaseSearchModel | None: The document if found, None otherwise
        """
        results = await cls.search_interface(
            {"query": {"ids": {"values": [id]}}}, size=1
        )
        return results[0].model if results else None

    @classmethod
    async def create(cls, **kwargs) -> T:
        obj = cls(**kwargs)
        await obj.save_interface()
        return obj

    async def update(self) -> T:
        await self.save_interface()
        return self

    @classmethod
    async def vector_search(
        cls,
        field: str,
        vector: list[float],
        *,
        k: int = 10,
        num_candidates: int = 100,
        score_threshold: float | None = None,
        filter_query: QueryBuilder | None = None,
        pre_filters: dict | None = None,
        kwargs_filter_mode: Literal["pre", "post", "both"] = "pre",
        **kwargs,
    ) -> list[ESManager.SearchResult]:
        """
        Perform a vector similarity search with optional filters.

        Args:
            field: Name of the dense vector field to search
            vector: Query vector to search with
            k: Number of results to return (default: 10)
            num_candidates: Number of candidates to consider (default: 100)
            score_threshold: Remove all results with scores below this threshold
            filter_query: Optional QueryBuilder with boolean filters to apply
            pre_filters: Additional filters to apply before the knn search
            kwargs_filter_mode: Whether to apply additional filters in kwargs before, after, or both
            **kwargs: Field-value pairs to filter results (e.g., category="books")

        Returns:
            list[ESManager.SearchResult]: List of search results with scores and metadata
        """
        query = cls.query()
        query.knn(
            field=field,
            vector=vector,
            k=k,
            num_candidates=num_candidates,
            **(pre_filters or {}),
            **(kwargs if kwargs_filter_mode in ["pre", "both"] else {}),
        )

        if kwargs:
            query.filter(**(kwargs if kwargs_filter_mode in ["post", "both"] else {}))

        if filter_query is not None:
            query.merge(filter_query)

        results = await query.execute()

        if score_threshold is not None:
            return [r for r in results if r.score >= score_threshold]
        else:
            return results

    @classmethod
    async def hybrid_search(
        cls,
        text_field: str,
        text: str,
        vector_field: str,
        vector: list[float],
        *,
        k: int = 10,
        num_knn_candidates: int = 100,
        lexical_weight: float = 0.5,
        rrf_weight: float = 1.0,
        rrf_k: int = 60,
        score_threshold: float | None = None,
        filter_query: QueryBuilder | None = None,
        knn_pre_filters: dict | None = None,
        kwargs_filter_mode: Literal["pre", "post", "both"] = "pre",
        **kwargs,
    ) -> list[ESManager.SearchResult]:
        """
        Perform a hybrid search that fuses lexical and vector search results with RRF.

        Args:
            text_field: Name of the `text field to search.
            text: The text query for lexical search.
            vector_field: Name of the dense vector field to search.
            vector: The query vector.
            k: Number of results to return for the vector portion.
            num_knn_candidates: Number of vector candidates for the knn portion.
            lexical_weight: Weight for the lexical search results (0.0 to 1.0) vs. vector search.
            rrf_weight: Weight for the RRF score (0.0 to 1.0) vs. normalized BM25 or knn score.
            rrf_k: RRF constant to dampen the reciprocal rank contribution.
            score_threshold: Remove all results with scores below this threshold.
            filter_query: Optional QueryBuilder with boolean filters to apply
            knn_pre_filters: Additional filters to apply before the knn search.
            kwargs_filter_mode: Whether to apply additional filters in kwargs before, after, or both for knn search.
            **kwargs: Additional filters to apply

        Returns:
            List of fused search results, sorted by RRF-derived score.
        """
        if not 0 <= lexical_weight <= 1:
            raise ValueError("lexical_weight must be between 0 and 1")
        if not 0 <= rrf_weight <= 1:
            raise ValueError("rrf_weight must be between 0 and 1")

        # Use same size k for both searches
        lexical_qb = cls.query().size(k)
        lexical_qb.should(**{text_field: text})

        vector_qb = cls.query().knn(
            field=vector_field,
            vector=vector,
            k=k,
            num_candidates=num_knn_candidates,
            **(knn_pre_filters or {}),
            **(kwargs if kwargs_filter_mode in ["pre", "both"] else {}),
        )

        # Apply filters to both queries
        if kwargs:
            lexical_qb.filter(**kwargs)
            vector_qb.filter(
                **(kwargs if kwargs_filter_mode in ["post", "both"] else {})
            )

        if filter_query is not None:
            lexical_qb.merge(filter_query)
            vector_qb.merge(filter_query)

        lexical_query_dict = lexical_qb.build()
        vector_query_dict = vector_qb.build()

        # Execute searches
        [lexical_hits, vector_hits] = await cls.multi_search_interface(
            [lexical_query_dict, vector_query_dict]
        )

        if not lexical_hits and not vector_hits:
            return []

        fused_scores: dict[str, float] = {}
        fused_models: dict[str, ESManager.SearchResult] = {}

        def apply_rrf(results: list[ESManager.SearchResult], is_lexical: bool):
            if not results:
                return

            weight = lexical_weight if is_lexical else (1 - lexical_weight)
            # Calculate max score once
            max_score = max(r.score for r in results)
            min_score = min(r.score for r in results)
            score_range = max_score - min_score

            for rank, _hit in enumerate(results):
                _doc_id = _hit.model.id
                # Combine RRF with original score
                rrf_score = weight * (1.0 / (rrf_k + rank + 1))

                # More robust score normalization
                norm_score = (
                    weight * ((_hit.score - min_score) / score_range)
                    if score_range > 0
                    else 0
                )

                combined_score = (
                    rrf_weight * rrf_score + (1.0 - rrf_weight) * norm_score
                )
                fused_scores[_doc_id] = fused_scores.get(_doc_id, 0.0) + combined_score
                fused_models[_doc_id] = _hit

        # Apply RRF and score normalization to both result sets
        apply_rrf(lexical_hits, is_lexical=True)
        apply_rrf(vector_hits, is_lexical=False)

        # Sort all results by the fused score in descending order.
        # Then create a final list of ESManager.SearchResult objects in that order.
        all_doc_ids = list(fused_scores.keys())
        all_doc_ids.sort(key=lambda _doc_id: fused_scores[_doc_id], reverse=True)

        fused_results: list[ESManager.SearchResult] = []
        for doc_id in all_doc_ids:
            hit = fused_models[doc_id]
            # You can store the final fused score somewhere if you like;
            # for now, just keep the original ESManager.SearchResult structure.
            fused_results.append(
                ESManager.SearchResult(
                    model=hit.model,
                    score=fused_scores[doc_id],
                    total=hit.total,  # or sum of total hits, etc.
                    response_uuid=hit.response_uuid,
                )
            )

        if score_threshold is not None:
            # Filter out results below the threshold
            fused_results = [r for r in fused_results if r.score >= score_threshold]

        # Return only the top k results overall
        return fused_results[:k]

    @classmethod
    async def lexical_search(
        cls,
        field: str,
        text: str,
        *,
        k: int = 10,
        score_threshold: float | None = None,
        filter_query: QueryBuilder | None = None,
        **kwargs,
    ) -> list[ESManager.SearchResult]:
        """
        Perform a lexical (text-based) search.

        Args:
            field: Name of the text field to search
            text: The text query to search for
            k: Number of results to return
            score_threshold: Remove all results with scores below this threshold
            filter_query: Optional QueryBuilder with boolean filters to apply
            **kwargs: Field-value pairs to filter results (e.g., category="books")

        Returns:
            list[ESManager.SearchResult]: List of search results with scores and metadata
        """
        query = cls.query().size(k)
        query.should(**{field: text})

        if kwargs:
            query.filter(**kwargs)

        if filter_query is not None:
            query.merge(filter_query)

        results = await query.execute()
        if score_threshold is not None:
            return [r for r in results if r.score >= score_threshold]
        else:
            return results

    async def save_interface(self, **kwargs) -> None:
        """
        Save/update the document in Elasticsearch.

        Args:
            **kwargs: Additional parameters to pass to ES index API
        """
        await ESManager.index(self, **kwargs)

    @classmethod
    async def search_interface(
        cls, query: dict, *, size: int = 10, from_: int = 0, **kwargs
    ) -> list[ESManager.SearchResult]:
        """
        Search for documents of this model type.

        Args:
            query: Elasticsearch query dict
            size: Number of results to return
            from_: Starting offset
            **kwargs: Additional parameters to pass to search API

        Returns:
            list[ESManager.SearchResult]: List of search results with scores and metadata
        """
        return await ESManager.search(cls, query, size=size, from_=from_, **kwargs)

    @classmethod
    async def multi_search_interface(
        cls, queries: list[dict], **kwargs
    ) -> list[list[ESManager.SearchResult]]:
        """
        Execute multiple searches in parallel.

        Args:
            queries: List of Elasticsearch query dicts
            **kwargs: Additional parameters to pass to msearch API

        Returns:
            list[list[ESManager.SearchResult]]: List of search result lists, each containing
                results with scores and metadata
        """
        return await ESManager.multi_search(cls, queries, **kwargs)

    @classmethod
    async def bulk_save_interface(
        cls, models: list["BaseSearchModel"], *, refresh: bool = False, **kwargs
    ) -> dict:
        """
        Bulk save multiple instances of this model.

        Args:
            models: List of model instances to save
            refresh: Whether to refresh the index immediately
            **kwargs: Additional parameters to pass to bulk API

        Returns:
            dict: Elasticsearch bulk operation response
        """
        return await ESManager.bulk_index(models, refresh=refresh, **kwargs)
