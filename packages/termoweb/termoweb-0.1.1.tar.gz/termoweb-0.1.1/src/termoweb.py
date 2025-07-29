import httpx
import time
from typing import Optional, Dict, Any


class TermowebError(Exception):
    """Base exception for Termoweb API errors"""
    pass


class AuthenticationError(TermowebError):
    """Raised when authentication fails"""
    pass


class APIError(TermowebError):
    """Raised when API requests fail"""
    pass


class Termoweb:
    BASE_URL = "https://control.termoweb.net"
    TERMOWEB_TOKEN = "Basic NTIxNzJkYzg0ZjYzZDZjNzU5MDAwMDA1OmJ4djRaM3hVU2U="
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.user_token: Optional[str] = None
        self.sid: Optional[str] = None
        self.device_id: Optional[str] = None


    def get_time(self) -> int:
        return int(time.time() * 1000)
    
    def _make_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                     data: Optional[Dict[str, Any]] = None, 
                     json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Generic HTTP request handler with error handling"""
        try:
            response = httpx.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json
            )
            
            if int(response.status_code / 100) != 2:
                if response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed: {response.status_code} - {response.text}")
                else:
                    error_msg = f"{method} {url} failed: {response.status_code} - {response.text}"
                    raise APIError(error_msg)
            
            return response
            
        except httpx.RequestError as e:
            raise APIError(f"HTTP request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise APIError(f"HTTP error: {str(e)}")
    
    def connect(self) -> None:
        response = self._make_request(
            method='POST',
            url=f'{self.BASE_URL}/client/token',
            data={
                'username': self.email,
                'password': self.password,
                'grant_type': 'password'
            },
            headers={
                "Authorization": self.TERMOWEB_TOKEN
            }
        )
        
        self.user_token = response.json()['access_token']

        response = self._make_request(
            method='GET',
            url=f'{self.BASE_URL}/api/v2/devs/',
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.device_id = response.json()['devs'][0]['dev_id']
        
    def get_devices(self) -> Dict[int, Dict[str, Any]]:
        response = self._make_request(
            method='GET',
            url=f'{self.BASE_URL}/api/v2/devs/{self.device_id}/mgr/nodes',
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        
        nodes_id = [node['addr'] for node in response.json().get('nodes', []) if node['type'] == 'htr']

        heaters = {}
        for node_id in nodes_id:
            response = self._make_request(
                method='GET',
                url=f'{self.BASE_URL}/api/v2/devs/{self.device_id}/htr/{node_id}/settings',
                headers={"Authorization": f"Bearer {self.user_token}"},
            )
            
            data = response.json()
            heaters[node_id] = {
                "name": data.get("name", "Unknown"),
                "mode": data.get("mode", None),
                "target_temp": data.get("stemp", None),
                "room_temp": data.get("mtemp", None),
            }
        return heaters
        
    def set_heater(self, heater_id: int, mode: str, target_temp: float) -> None:
        settings = {
            "mode": mode,
            "units": "C",
            "stemp": str(target_temp)
        }
        
        self._make_request(
            method='POST',
            url=f"{self.BASE_URL}/api/v2/devs/{self.device_id}/htr/{heater_id}/settings",
            json=settings,
            headers={"Authorization": f"Bearer {self.user_token}"})