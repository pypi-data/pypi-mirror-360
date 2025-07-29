import asyncio
import copy
import json
from typing import List, Text, Tuple

import duckdb
import rich.console

import dvs.utils.sql_stmts as SQL_STMTS
from dvs.types.columns import (
    COLUMN_NAMES_WITH_EMBEDDING,
    COLUMN_NAMES_WITHOUT_EMBEDDING,
)
from dvs.types.document import Document
from dvs.types.point import Point
from dvs.utils.display import DISPLAY_SQL_QUERY


async def vector_search(
    vector: List[float],
    *,
    top_k: int,
    embedding_dimensions: int,
    documents_table_name: Text,
    points_table_name: Text,
    conn: "duckdb.DuckDBPyConnection",
    with_embedding: bool = True,
    debug: bool = False,
    console: rich.console.Console | None = None,
) -> list[tuple["Point", "Document", float]]:
    """
    Perform a vector similarity search in a DuckDB database.

    This function executes a vector similarity search using the provided embedding vector
    against the points stored in the specified DuckDB table. It returns the top-k most
    similar points along with their associated documents and relevance scores.

    Notes
    -----
    - The function uses array_cosine_similarity for calculating the similarity between vectors.
    - Results are ordered by descending relevance score.
    - The SQL query joins the points table with the documents table to retrieve associated document information.

    Examples
    --------
    >>> conn = duckdb.connect('my_database.duckdb')
    >>> query_vector = [0.1, 0.2, 0.3, ..., 0.5]  # 512-dimensional vector
    >>> results = await vector_search(
    ...     query_vector,
    ...     top_k=5,
    ...     embedding_dimensions=512,
    ...     documents_table_name='documents',
    ...     points_table_name='points',
    ...     conn=conn
    ... )
    >>> for point, document, score in results:
    ...     print(f"Point ID: {point.point_id}, Score: {score}, Document: {document.name}")

    See Also
    --------
    ensure_vectors : Function to prepare input vectors for search.
    api_search : API endpoint that utilizes this vector search function.
    """  # noqa: E501

    output: List[Tuple["Point", "Document", float]] = []

    column_names_expr = ", ".join(
        list(
            COLUMN_NAMES_WITH_EMBEDDING
            if with_embedding
            else COLUMN_NAMES_WITHOUT_EMBEDDING
        )
    )
    query = SQL_STMTS.SQL_STMT_VSS.format(
        top_k=top_k,
        column_names_expr=column_names_expr,
        embedding_dimensions=embedding_dimensions,
        documents_table_name=documents_table_name,
        points_table_name=points_table_name,
    )
    params = [vector]
    if debug and console:
        console.print(
            "\nPerforming vector similarity search with SQL:\n"
            + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
        )

    # Fetch results
    result = await asyncio.to_thread(conn.execute, query, params)
    fetchall_result = await asyncio.to_thread(result.fetchall)

    # Convert to output format
    assert result.description is not None
    for row in fetchall_result:
        row_dict = dict(zip([desc[0] for desc in result.description], row))
        row_dict_doc = copy.deepcopy(row_dict)
        row_dict_pt = row_dict
        row_dict_pt["metadata"] = json.loads(
            row_dict_pt.pop("point_metadata", None) or "{}"
        )
        row_dict_doc["metadata"] = json.loads(
            row_dict_doc.pop("document_metadata", None) or "{}"
        )
        row_dict_pt["embedding"] = row_dict_pt.get("embedding") or []

        _point = Point.model_validate(row_dict_pt)
        _document = Document.model_validate(row_dict_doc)
        output.append((_point, _document, row_dict["relevance_score"]))

    return output
