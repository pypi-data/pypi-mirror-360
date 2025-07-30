import base64
import json
from .client import Client

def create_uc6(client:Client, workflow_name:str, start_date:str, end_date:str, geometry:str):
    def get_product_info(response:dict):
        item = response['payload'][0]
        return item['id'], item['persistentID'], item['metadata']['Title'][0]['values'][0]
    persistent_ids = []
    titles = []
    products = []
    metadata = []
    ids = [100, 104]   # temperature and precipitation (hourly)
    for id in ids:                                        
        _, response = client.kg_search_dataset([id])
        id, persistent_id, title = get_product_info(response)

        data = {
        "id": id,
        "datasetPersistentId": persistent_id,
        "requestOptions": {
            "Geometry": [
                geometry
            ],
            "Date": [
            start_date,
            end_date
            ]
        }
        }
        _, response = client.kg_search_dataset_breakdown_post(id, data)
        response["payload"]["products"].append({"extraInfo": {"datasetName": title}})

        temp = []
        for item in response['payload']['products']:
            if 'id' in item:
                temp.append(item['id'])
        products.append(temp)
        titles.append(title)
        persistent_ids.append(persistent_id)
        metadata.append(response['payload']['products'])

        scripts = []
        for id, persistent_id, product_list in zip(ids, persistent_ids, products):
            data = {
                "datasetId": id,
                "datasetPersistentId": persistent_id,
                "requestOptions": {
                    "ProductID": product_list,
                    "Compress": [
                        "True"
                    ]
                }
            }
            _, response = client.kg_generate_api_call(id, data)
            scripts.append(response['payload'])

            encoded_scripts = []
            for script in scripts:
                encoded_scripts.append(base64.b64encode(script.encode("ascii")).decode("ascii"))
            encoded_metadata = base64.b64encode(json.dumps(metadata).encode("ascii")).decode("ascii")

            data = {
                "name": workflow_name,
                "query": encoded_scripts,
                "meta": encoded_metadata
            }
            client.workflow_create(data)

            return client.get_workflow_id(workflow_name, openeo.status_type.DRAFT.value, openeo.cfs_type.FALSE.value)