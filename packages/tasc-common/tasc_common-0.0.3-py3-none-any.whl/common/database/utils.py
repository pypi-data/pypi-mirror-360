from typing import Tuple, Optional, List

import networkx as nx
from annotated_types import MaxLen
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined, MultiHostUrl
from sqlmodel import SQLModel, Session, select
from sqlmodel.main import SQLModelMetaclass
from sqlalchemy import inspect


def get_max_len(field: FieldInfo) -> Optional[int]:
    return next(
        (meta.max_length for meta in field.metadata if isinstance(meta, MaxLen)), None
    )


def find_primary_key(cls: SQLModelMetaclass) -> Optional[str]:
    return next(
        (
            field_id
            for field_id, field_info in cls.__fields__.items()
            if field_info.primary_key is not PydanticUndefined
            and field_info.primary_key
        ),
        None,
    )

def build_dependency_graph(engine) -> Tuple[nx.DiGraph, nx.DiGraph]:
    inspector = inspect(engine)
    graph = nx.DiGraph()
    reverse_graph = nx.DiGraph()

    for table_name in inspector.get_table_names():
        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            referred_table = fk["referred_table"]
            graph.add_edge(referred_table, table_name)
            reverse_graph.add_edge(table_name, referred_table)

    return graph, reverse_graph


def topological_sort(graph: nx.DiGraph) -> List[str]:
    try:
        return list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        raise ValueError(
            "There is a cycle in the dependency graph, or not all nodes were reachable."
        )


def delete_object_with_dependencies(session: Session, obj: SQLModel) -> None:
    _, reverse_graph = build_dependency_graph(session.bind)

    table_name = obj.__tablename__
    primary_key = find_primary_key(obj.__class__)
    if primary_key is None:
        raise ValueError(f"No primary key found for {obj.__class__.__name__}")

    record_id = getattr(obj, primary_key)

    dependency_order = list(nx.dfs_postorder_nodes(reverse_graph, source=table_name))

    try:
        for dependent_table in dependency_order:
            if dependent_table != table_name and reverse_graph.has_edge(
                dependent_table, table_name
            ):
                table = SQLModel.metadata.tables[dependent_table]
                foreign_key = next(
                    fk
                    for fk in table.foreign_keys
                    if fk.column.table.name == table_name
                )
                dependent_records = session.exec(
                    select(table).where(foreign_key.column == record_id)
                ).all()
                for record in dependent_records:
                    session.delete(record)

        # Delete the original object
        session.delete(obj)

        session.commit()
    except Exception as e:
        session.rollback()
        raise RuntimeError(
            f"Failed to delete object and its dependencies: {str(e)}"
        ) from e


def build_database_url(
    username: str,
    password: str,
    server: str,
    port: int,
    db: str,
    asyncpg: bool = True,
) -> MultiHostUrl:
    return MultiHostUrl.build(
        scheme="postgresql+asyncpg" if asyncpg else "postgresql",
        username=username,
        password=password,
        host=server,
        port=port,
        path=db,
    )
