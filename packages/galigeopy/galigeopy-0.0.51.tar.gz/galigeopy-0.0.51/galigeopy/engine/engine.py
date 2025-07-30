from pydantic import BaseModel

class Engine:
    def __init__(self, engine_type:str,  parameters: dict, base_model: BaseModel, auto_test:bool=True):
        self._engine_type = engine_type
        self._parameters = parameters
        self._base_model = base_model
        self._check_parameters()
        if auto_test:
            self._check_status()

    @property
    def engine_type(self): return self._engine_type
    @property
    def parameters(self): return self._parameters

    def _check_parameters(self):
        try:
            self._base_model(**self._parameters)
        except Exception as e:
            raise ValueError(f"Invalid parameters: {e}")
        
    def list_funtions(self):
        raise NotImplementedError("This method should be implemented in subclasses.")

    def run_function(self, function_name: str, *args, **kwargs):
        if not hasattr(self, function_name):
            raise AttributeError(f"Function '{function_name}' is not defined in the engine.")
        return getattr(self, function_name)(*args, **kwargs)
    
    def _check_status(self):
        raise NotImplementedError("This method should be implemented in subclasses to check the engine status.")
    
        