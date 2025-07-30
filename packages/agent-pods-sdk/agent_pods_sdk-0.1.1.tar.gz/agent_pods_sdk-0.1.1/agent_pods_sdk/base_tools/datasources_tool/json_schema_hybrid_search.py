def build_json_schema_hybrid_search(
    datasource_names: list[str],
    path_prefix_options: list[str] = [""],
    sparse_weight_options: list[float] = [1, 0.4, 0],
    dense_weight_options: list[float] = [1, 0.6, 0],
    limit: int = 4,
) -> dict:
    """
    Builds the JSON schema for the hybrid search function.

    Returns:
        dict: The JSON schema for the hybrid search function.
    """
    return {
        "type": "object",
        "properties": {
            "datasource_names": {
                "type": "array",
                "description": "A list of data sources to filter the search results.",
                "items": {
                    "type": "string",
                    "enum": datasource_names,
                },
            },
            "query": {
                "type": "string",
                "description": "The query string to search within the files.",
            },
            "limit": {
                "type": "integer",
                "description": "The maximum number of results to return.",
                "default": limit,
            },
            "path_prefix": {
                "type": "string",
                "description": "A prefix filter for file paths. Only files with paths matching this prefix will be searched.",
                "enum": path_prefix_options,
            },
            "dense_weight": {
                "type": "number",
                "description": "The weight for dense (semantic) search.",
                "enum": dense_weight_options,
            },
            "sparse_weight": {
                "type": "number",
                "description": "The weight for sparse (keyword) search.",
                "enum": sparse_weight_options,
            },
        },
        "required": [
            "query",
            "datasource_names",
            "dense_weight",
            "sparse_weight",
            "limit",
            "path_prefix",
        ],
        "additionalProperties": False,
    }
