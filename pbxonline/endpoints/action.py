from typing import Optional

from pbxonline.models.base import ObjectListModel, BaseModel
from .base import APIEndpoint
from pbxonline.models.utils import construct_object_from_data, construct_error_from_data
from pbxonline.utils import request_not_succesful

class ActionEndpoint(APIEndpoint):
    
    def __init__(self, api: object) -> None:
        endpoint = 'action'
        super().__init__(api, endpoint)
    
    def get_ongoing_calls(self) -> ObjectListModel:
        
        status, headers, resp_json = self.api.get( f'{self.endpoint}/conversation')
        if request_not_succesful(status): return construct_error_from_data(resp_json)
        
        return construct_object_from_data(resp_json['results'])
    
    def start_call(self, sipaccount_id, call_to) -> BaseModel:
        
        status, headers, resp_json = self.api.post( f'{self.endpoint}/conversation', data={'call-1' : { 'origin': sipaccount_id, 'destination': call_to }})
        if request_not_succesful(status): return construct_error_from_data(resp_json)
        
        return construct_object_from_data(resp_json[0])
    
    def end_call(self, call_id) -> BaseModel:
        
        status, headers, resp_json = self.api.delete( f'{self.endpoint}/conversation', data={'ID' : call_id})
        if request_not_succesful(status): return construct_error_from_data(resp_json)
        
        return construct_object_from_data(resp_json)