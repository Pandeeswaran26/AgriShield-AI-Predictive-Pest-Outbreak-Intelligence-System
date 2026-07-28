import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "precipitation",
        ],
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    current = response.json()["current"]

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "rainfall": current["precipitation"],
    }