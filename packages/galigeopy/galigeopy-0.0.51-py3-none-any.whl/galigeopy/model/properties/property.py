class Property:
    def __init__(self, column, dtype=str, json_info: dict[str, str] | None= None, rename=None, agg_function:str|None=None):
        self._column = column
        self._dtype = dtype
        self._json_info = json_info
        self._rename = rename
        self._agg_function = agg_function

    @property
    def column(self): return self._column
    @property
    def dtype(self): return self._dtype
    @property
    def json_info(self): return self._json_info
    @property
    def rename(self): return self._rename
    @property
    def agg_function(self): return self._agg_function

    # setters
    @column.setter
    def column(self, column): self._column = column
    @dtype.setter
    def dtype(self, dtype): self._dtype = dtype
    @json_info.setter
    def json_info(self, json_info): self._json_info = json_info
    @rename.setter
    def rename(self, rename): self._rename = rename
    @agg_function.setter
    def agg_function(self, agg_function): self._agg_function = agg_function

    def to_sql(self, prefix=None):
        # Build the base column reference, possibly with a prefix (e.g. table alias)
        col_ref = f"{prefix}.{self._column}" if prefix else self._column

        # If json_info is provided, extract the key from the JSON column
        if self._json_info:
            json_key = self._json_info["key"]
            json_dtype = self._json_info.get("dtype", "text")
            col_ref = f"({col_ref} ->> '{json_key}')::{json_dtype}"

        # Apply aggregation function if specified
        if self._agg_function:
            col_ref = f"{self._agg_function.upper()}({col_ref})"

        # Apply aliasing: use the rename if provided, otherwise fallback to column or json key
        alias = self.get_name()

        return f"{col_ref} AS {alias}"
    
    def get_name(self):
        return self._rename or self._json_info.get("key", 'undefined') if self._json_info else self._column
    
    def get_type(self):
        return self._dtype if self._dtype.lower() != "jsonb" else self._json_info.get("dtype", "text")
    
    def getDefaultAggFunction(self):
        return "SUM"
    
    def getAllAggFunctions(self):
        return ["SUM", "AVG", "COUNT", "MIN", "MAX"]