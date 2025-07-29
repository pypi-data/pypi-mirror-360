import respx
from httpx import Response
from src.termoweb import Termoweb
import json


@respx.mock
def test_get_devices_success():
    mock_email = "user@example.com"
    mock_password = "securepassword"
    mock_token = "mocked_access_token"
    mock_device_id = "mock_device_123"
    
    respx.post("https://control.termoweb.net/client/token").mock(
        return_value=Response(200, json={"access_token": mock_token})
    )
    
    respx.get("https://control.termoweb.net/api/v2/devs/").mock(
        return_value=Response(200, json={"devs": [{"dev_id": mock_device_id}]})
    )
    
    respx.get(f"https://control.termoweb.net/api/v2/devs/{mock_device_id}/mgr/nodes").mock(
        return_value=Response(200, json={
            "nodes": [
                {"type": "htr", "addr": 2, "name": "Heater 1", "installed": True, "lost": False, "hw_version": "1.5", "fw_version": "1.12"},
                {"type": "htr", "addr": 3, "name": "Heater 2", "installed": True, "lost": False, "hw_version": "1.5", "fw_version": "1.11"},
            ]
        })
    )
    
    respx.get(f"https://control.termoweb.net/api/v2/devs/{mock_device_id}/htr/2/settings").mock(
        return_value=Response(200, json={"name": "Heater 1", "mode": "off", "stemp": "20.0", "mtemp": "26.7"})
    )
    respx.get(f"https://control.termoweb.net/api/v2/devs/{mock_device_id}/htr/3/settings").mock(
        return_value=Response(200, json={"name": "Heater 2", "mode": "off", "stemp": "20.0", "mtemp": "27.0"})
    )
    
    client = Termoweb(mock_email, mock_password)
    client.connect()
    heaters = client.get_devices()
    
    assert len(heaters) == 2
    assert heaters[2]["name"] == "Heater 1"
    assert heaters[2]["mode"] == "off"
    assert heaters[2]["target_temp"] == "20.0"
    assert heaters[2]["room_temp"] == "26.7"
    assert heaters[3]["name"] == "Heater 2"


@respx.mock
def test_set_heater_success():
    mock_email = "user@example.com"
    mock_password = "securepassword"
    mock_token = "mocked_access_token"
    mock_device_id = "mock_device_123"
    heater_id = 2
    mode = "on"
    target_temp = 22.5
    
    respx.post("https://control.termoweb.net/client/token").mock(
        return_value=Response(200, json={"access_token": mock_token})
    )
    
    respx.get("https://control.termoweb.net/api/v2/devs/").mock(
        return_value=Response(200, json={"devs": [{"dev_id": mock_device_id}]})
    )
    
    respx.post(f"https://control.termoweb.net/api/v2/devs/{mock_device_id}/htr/{heater_id}/settings").mock(
        return_value=Response(200, json={"status": "success"})
    )
    
    client = Termoweb(mock_email, mock_password)
    client.connect()
    client.set_heater(heater_id, mode, target_temp)
    
    request = respx.calls[-1].request
    assert request.method == "POST"
    assert request.url == f"https://control.termoweb.net/api/v2/devs/{mock_device_id}/htr/{heater_id}/settings"
    assert request.headers["Authorization"] == f"Bearer {mock_token}"
    
    payload = json.loads(request.content)
    assert payload["mode"] == mode
    assert payload["units"] == "C"
    assert payload["stemp"] == str(target_temp)
