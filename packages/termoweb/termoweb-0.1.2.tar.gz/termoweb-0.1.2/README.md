# Termoweb

Python client library for controlling Termo thermostats via web interface.

## Installation

```bash
pip install termoweb
```

## Usage

```python
from termoweb import Termoweb

# Initialize client with your credentials
client = Termoweb(email="your_email@example.com", password="your_password")

# Connect to the service
client.connect()

# Get all heaters/radiators
heaters = client.get_devices()
print(heaters)

# Set heater temperature and mode
client.set_heater(heater_id=1, mode="heat", target_temp=21.5)
```

## API Reference

### `Termoweb(email, password)`
Initialize the client with your Termoweb credentials.

### `connect()`
Authenticate and establish connection to the Termoweb service.

### `get_devices()`
Returns a dictionary of all connected heaters with their current settings:
```python
{
    1: {
        "name": "Living Room",
        "mode": "heat",
        "target_temp": 21.0,
        "room_temp": 20.5
    }
}
```

### `set_heater(heater_id, mode, target_temp)`
Set the mode and target temperature for a specific heater.

## Exception Handling

The library includes custom exceptions:
- `TermowebError`: Base exception
- `AuthenticationError`: Authentication failures
- `APIError`: API request failures

## Supported Devices

| Device Type       | Supported |
|-------------------|-----------|
| Heaters/Radiators | ✅        |
| Thermostats       | ❌        |
| Power Monitors    | ❌        |