import requests
import json
import urllib.parse
from enum import Enum
from typing import Tuple, List, Dict, Any

class status_type(Enum):
    DRAFT = "DRAFT"
    COMPILING = "COMPILING"
    COMPILED = "COMPILED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    DSL_ERRROR = "DSL_ERROR" 

class cfs_type(Enum):
    TRUE = "true"
    FALSE = 'false'

class Client:
    def __init__(self, env_url:str, username:str, password:str, otp:str|None=None):
        self.env_url = env_url
        self.username = username
        self.password = password
        self.otp = otp
        self.bearer_token, self.refresh, self.expiration, self.refresh_expiration = self.get_token(username, password, otp)

    def handle_token(self):
        # more logic needed here
        self.bearer_token, self.refresh, self.expiration, self.refresh_expiration = self.get_token(self.username, self.password, self.otp)
        
    def get_token(self, username:str, password:str, otp:str|None=None) -> Tuple[str, str]|None:    
        url = f'{self.env_url}/Auth/Token'
        headers = {
            "accept": "*/*",
            "username": username,
            "password": password,
        }
        if otp is not None:
            headers['otp'] = otp  
        data = {}

        try:
            response = requests.post(url, headers=headers, data=data)
            token = json.loads(response.text)['access_token']
            refresh = json.loads(response.text)['refresh_token']
            expiration = json.loads(response.text)['expires_in']
            refresh_expiration = json.loads(response.text)['refresh_expires_in']
            return (token, refresh,expiration, refresh_expiration)
        except:
            return None
        
    def refresh_token(self, refresh_token:str) -> Tuple[str, str]|None:
        url = f'{self.env_url}/Auth/Token/Refresh?refresh_token={refresh_token}'
        headers = {
            "accept": "*/*",
        }
        data = {}

        try:
            response = requests.post(url, headers=headers, data=data)
            token = json.loads(response.text)['access_token']
            refresh = json.loads(response.text)['refresh_token']
            return (token, refresh)
        except:
            return None
        
    def list_workflows(self, status:str, cfs:str) -> List[Tuple[str, str]]|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows?status={status}&withCfs={cfs}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response = json.loads(response.text)
            mapping = []
            for item in response:
                mapping.append((item['name'], item['id']))
            return mapping
        except:
            return None

    def get_workflow_id(self, workflow_name:str, status:str, cfs:str) -> str|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows?status={status}&withCfs={cfs}'
        headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response = json.loads(response.text)
            for item in response:
                if item['name'] == workflow_name:  
                    return item['id'] 
        except:
            return None

    def get_workflow_info(self, workflow_id:str) -> Dict[str, Any]|None :
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows/{workflow_id}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            info = json.loads(response.text)
            return info
        except:
            return None
        
    def workflow_start(self, workflow_id:str) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows/{workflow_id}/start'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            return (response.status_code, response.text)
        except:
            return None

    def workflow_stop(self, workflow_id:str) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows/{workflow_id}/stop'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            return (response.status_code, response.text)
        except:
            return None
  
    def workflow_delete(self, workflow_id:str) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows/{workflow_id}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.delete(url, headers=headers)
            return (response.status_code, response.text)
        except:
            return None
        
    def workflow_create(self, data:dict) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'{self.env_url}/Kafka/workflow'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            return (response.status_code, response.text)
        except:
            return None
        
    def workflow_update(self, workflow_id:str, data:dict) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'{self.env_url}/DSL/dsl-api/workflows/{workflow_id}/update'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            return (response.status_code, response.text)
        except:
            return None
        
    def workflow_update_dsl(self, workflow_id:str, data:dict) -> Tuple[int, str]|None:
        self.handle_token()
        url = f'https://dsl-api.apps.eo4eu.eu/my/workflows/{workflow_id}/update'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.patch(url, headers=headers, json=data)
            return (response.status_code, response.text)
        except:
            return None

    def list_s3_bucket(self, s3_bucket_name:str) -> List[Any]|None:
        self.handle_token()
        url = f'{self.env_url}/S3/bucket/{s3_bucket_name}/files'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            content = json.loads(response.text)
            return content
        except:
            return None

    def kg_advanced_query(self, query:str, sources:str):
        self.handle_token()
        formated_query = urllib.parse.quote(query)
        formated_sources = urllib.parse.quote(sources)
        url = f'{self.env_url}/KG/api/execute-advanced-query?query={formated_query}&sources={formated_sources}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            return (response.status_code, json.loads(response.text))
        except:
            return None

    def kg_search_dataset(self, values:list):
        self.handle_token()
        formated_values = ','.join(map(str, values))
        url = f'{self.env_url}/KG/api/search-DataSet?values={formated_values}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            return (response.status_code, json.loads(response.text))
        except:
            return None

    def kg_search_dataset_breakdown_get(self, value:int):
        self.handle_token()
        url = f'{self.env_url}/KG/api/search-dataset-breakdown/{value}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            return (response.status_code, json.loads(response.text))
        except:
            return None

    def kg_search_dataset_breakdown_post(self, value:int, data:dict):
        self.handle_token()
        url = f'{self.env_url}/KG/api/search-dataset-breakdown/{value}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            return (response.status_code, json.loads(response.text))
        except:
            return None

    def kg_generate_api_call(self, value:int, data:dict):
        self.handle_token()
        url = f'{self.env_url}/KG/api/generate-api-call?id={value}'
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            return (response.status_code, json.loads(response.text))
        except:
            return None

