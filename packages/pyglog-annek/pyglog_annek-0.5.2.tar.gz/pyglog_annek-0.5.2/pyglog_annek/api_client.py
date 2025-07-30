import requests
import logging
from typing import Dict, Any, Optional


class GraylogAPIClient:
    """Client for interacting with Graylog API."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.logger = logging.getLogger("pyglog")
        
        # Disable SSL warnings for self-signed certificates
        requests.packages.urllib3.disable_warnings(
            category=requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to Graylog API."""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        headers = kwargs.pop('headers', {})
        headers.setdefault('Accept', 'application/json')
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                auth=(self.token, "token"),
                verify=False,
                **kwargs
            )
            
            self.logger.info(f"{method} request to {url} returned {response.status_code}")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to {url} failed: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request to API."""
        return self._make_request('GET', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request to API."""
        return self._make_request('PUT', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request to API."""
        return self._make_request('POST', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request to API."""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def get_all_sidecars(self) -> Dict[str, Any]:
        """Get all sidecars from API."""
        response = self.get('sidecars/all')
        return response.json()
    
    def get_sidecar_by_id(self, sidecar_id: str) -> Dict[str, Any]:
        """Get specific sidecar by ID."""
        response = self.get(f'sidecars/{sidecar_id}')
        return response.json()
    
    def get_configurations(self) -> Dict[str, Any]:
        """Get all sidecar configurations."""
        response = self.get('sidecar/configurations')
        return response.json()
    
    def get_configuration_by_id(self, config_id: str) -> Dict[str, Any]:
        """Get specific configuration by ID."""
        response = self.get(f'sidecar/configurations/{config_id}')
        return response.json()
    
    def update_sidecar_configurations(self, data: Dict[str, Any], request_origin: str = "pyglog") -> requests.Response:
        """Update sidecar configuration assignments."""
        headers = {'X-Requested-By': request_origin}
        return self.put('sidecars/configurations', json=data, headers=headers)