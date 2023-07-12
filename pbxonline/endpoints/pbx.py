from typing import Optional

from pbxonline.models.base import ObjectListModel, BaseModel
from .base import APIEndpoint
from pbxonline.models.utils import construct_object_from_data, construct_error_from_data

class PBXEndpoint(APIEndpoint):
    
    def __init__(self, api: object) -> None:
        endpoint = 'pbx'
        super().__init__(api, endpoint)
        
    def get_sip_accounts(self) -> ObjectListModel:
        
        status, headers, resp_json = self.api.get( f'{self.endpoint}/sipaccount')
        if status > 299: return construct_error_from_data(resp_json)

        return construct_object_from_data(resp_json['results'])
    
    def get_did_numbers(self) -> ObjectListModel:
        
        status, headers, resp_json = self.api.get( f'{self.endpoint}/did')
        if status > 299: return construct_error_from_data(resp_json)

        return construct_object_from_data(resp_json['results'])