PYTHON_POSTGRES_TYPE = {
    "int": "INTEGER",
    "int64": "BIGINT",
    "float": "FLOAT",
    "float64": "DOUBLE PRECISION",
    "str": "TEXT",
    "bool": "BOOLEAN",
    "datetime": "TIMESTAMP",
    "date": "DATE",
    "time": "TIME",
    "dict": "JSON",
    "list": "ARRAY",
    "NoneType": "NULL",
    "object": "TEXT",
    "geometry": "GEOMETRY",
    "nan": "FLOAT",
}

def pythonTypeToPostgresType(python_type: str) -> str:
    """
    Convert a Python type to a PostgreSQL type.

    Args:
        python_type (str): The Python type as a string.

    Returns:
        str: The corresponding PostgreSQL type.
    """
    if python_type.lower() in PYTHON_POSTGRES_TYPE:
        return PYTHON_POSTGRES_TYPE[python_type.lower()]
    else:
        raise ValueError(f"Unsupported Python type: {python_type.lower()}")