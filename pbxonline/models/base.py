from typing import Union, Optional

class BaseModel:
    
    def __init__(self) -> None:
        self.has_error = False
        self.error = None
    
    def construct_from_response(self, resp_data: dict) -> Union['BaseModel', 'ObjectListModel']:
        """ Construct an object from the returned response data. """
        from .utils import construct_object_from_data
        return construct_object_from_data(resp_data)
         
    
    def construct_error_from_response(self, response: dict) -> 'BaseModel':
        """ Construct an error object from the returned response data and attach it to a BaseModel. """
        from .utils import construct_error_from_data
        return construct_error_from_data(response)
    
    def __getattr__(self, name: str) -> None:
        """ Gets called when an attribute is not found. Always returns None."""
        return None

class ObjectListModel(BaseModel):
    
    def __init__(self, list: Optional[list] = None) -> None:
        super().__init__()
        self.list = list if list else []

    def add(self, item: object) -> list:
        self.list.append(item)
        return self.list
    
    def remove(self, item: object) -> list:
        self.list.remove(item)
        return self.list
    
    def iterator(self) -> list:
        return self.list