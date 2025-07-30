from typing import List, Optional

import requests
from agents import FunctionTool
from loguru import logger
from pydantic import BaseModel

from .json_schema_hybrid_search import build_json_schema_hybrid_search


class DatasourcesSearchArgs(BaseModel):
    datasource_names: List[str]
    query: str
    limit: int
    path_prefix: str
    dense_weight: float
    sparse_weight: float


def _search_file_service(
    args: DatasourcesSearchArgs,
    url: str,
    alias: Optional[str] = None,
    token: Optional[str] = None,
) -> dict:
    datasource_names = args.datasource_names
    query = args.query
    limit = args.limit
    path_prefix = args.path_prefix
    dense_weight = args.dense_weight
    sparse_weight = args.sparse_weight

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "datasource_names": datasource_names,
        "query": query,
        "limit": limit,
        "dense_weight": dense_weight,
        "sparse_weight": sparse_weight,
        "path_prefix": path_prefix,
        "alias": alias,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {str(e)}")
        return {"error": f"HTTP Error: {str(e)}", "details": e.response.text}
    except Exception as e:
        logger.error(f"HTTP error occurred: {str(e)}")
        return {"error": str(e)}


def search_datasource_tool(
    allowed_datasources: list[str],
    file_service_search_url: str,
    alias: str,
    token: str,
    path_prefix: List[str] = [""],
) -> FunctionTool:
    """ """

    description = (
        "Performs a hybrid search inside a set of files using a combination of dense (semantic) and sparse (keyword-based) retrieval methods.\n\n"
        "The AI should select one of the following preset categories for `dense_weight` and `sparse_weight` based on the type of query:\n\n"
        "- Generic search (1.0, 1.0): Use this for most queries where both semantic meaning and exact keyword matching are equally important.\n"
        "- Exact text match (0.0, 1.0): Use this when looking for specific words, IDs, or names in structured documents like legal texts or logs.\n"
        "- Conceptual search (1.0, 0.5): Use this for abstract ideas, paraphrased wording, or queries where meaning matters more than exact words."
    )

    description += ", ".join([d[0] for d in allowed_datasources]) + "."

    async def tool_wrapper(ctx, tool_args_json: str):
        import json

        try:
            args_dict = json.loads(tool_args_json)
            args = DatasourcesSearchArgs(**args_dict)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input from the model: {str(e)}")
            raise ValueError(f"Invalid JSON input from the model: {str(e)}")
        return _search_file_service(args, file_service_search_url, alias, token)

    params_json_schema = build_json_schema_hybrid_search(
        datasource_names=allowed_datasources,
        path_prefix_options=path_prefix,
    )

    file_service_search_tool = FunctionTool(
        name="file_service_search",
        description=description,
        params_json_schema=params_json_schema,
        on_invoke_tool=tool_wrapper,
    )

    return file_service_search_tool
