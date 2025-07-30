import requests
from therix.core.constants import API_Endpoint

class ApiService:
    def __init__(self, therix_api_key):
        if not therix_api_key:
            raise ValueError("therix_api_key is required")
        self.therix_api_key = therix_api_key
        self.base_url = API_Endpoint.BASE_URL
        self.headers = {
            "THERIX_API_KEY": self.therix_api_key,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, payload=None, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=payload, headers=self.headers, params=params)
        return self._handle_response(response)

    def post(self, endpoint, payload):
        return self._request("POST", endpoint, payload)

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)
    
    def patch(self, endpoint, payload):
        return self._request("PATCH", endpoint, payload)

    def _handle_response(self, response):
        if response.status_code not in {200, 201}:
            if(response.status_code == 401):
                print(f"Error: {response.status_code}, Invalid API key")
            elif (response.status_code == 404):    
                print(f"Error: {response.status_code},Data Not Found")
            else:   
                print(f"Error: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
        return response.json()