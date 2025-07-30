import requests

class GraphBuilderSync:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def push_data(self, node_id, node_data):
        url = f"{self.api_url}/api/graphbuilder/sync"
        payload = {
            "node_id": node_id,
            "node_data": node_data
        }
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def pull_data(self, node_id=None):
        url = f"{self.api_url}/api/graphbuilder/sync"
        params = {}
        if node_id:
            params["node_id"] = node_id
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
