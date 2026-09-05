from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from zoneinfo import ZoneInfo

import requests
from fastapi import HTTPException

from app.model_loader import encoders

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SUPPORTED_LOCATION_NAMES = list(encoders["Location"].classes_)
_SUPPORTED_LOCATION_COORDS = None


def _request_json(url: str, params: dict):
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def _pick_hour_value(times: list[str], values: list[float], target_hour: int):
    if not times or not values:
        return None

    target_date = times[0][:10]
    day_values = []
    for timestamp, value in zip(times, values):
        if timestamp.startswith(target_date):
            day_values.append((timestamp, value))

    if not day_values:
        return None

    for timestamp, value in day_values:
        if int(timestamp[11:13]) == target_hour:
            return value

    closest_timestamp, closest_value = min(
        day_values,
        key=lambda item: abs(int(item[0][11:13]) - target_hour),
    )
    return closest_value


def _current_year_week(timezone_name: str):
    if timezone_name and timezone_name != "auto":
        try:
            now = datetime.now(ZoneInfo(timezone_name))
        except Exception:
            now = datetime.now()
    else:
        now = datetime.now()
    iso = now.isocalendar()
    return now.year, int(iso.week)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


STATIC_LOCATION_COORDS = [
    {"name": "Akola", "latitude": 20.7002, "longitude": 77.0082, "timezone": "Asia/Kolkata", "admin1": "Maharashtra", "country": "India"},
    {"name": "Coimbatore", "latitude": 11.0168, "longitude": 76.9558, "timezone": "Asia/Kolkata", "admin1": "Tamil Nadu", "country": "India"},
    {"name": "Cuttack", "latitude": 20.4625, "longitude": 85.8828, "timezone": "Asia/Kolkata", "admin1": "Odisha", "country": "India"},
    {"name": "Lam", "latitude": 16.3067, "longitude": 80.4365, "timezone": "Asia/Kolkata", "admin1": "Andhra Pradesh", "country": "India"},
    {"name": "Ludhiana", "latitude": 30.9010, "longitude": 75.8573, "timezone": "Asia/Kolkata", "admin1": "Punjab", "country": "India"},
    {"name": "Maruteru", "latitude": 16.6200, "longitude": 81.7400, "timezone": "Asia/Kolkata", "admin1": "Andhra Pradesh", "country": "India"},
    {"name": "Nagpur", "latitude": 21.1458, "longitude": 79.0882, "timezone": "Asia/Kolkata", "admin1": "Maharashtra", "country": "India"},
    {"name": "Palampur", "latitude": 32.1109, "longitude": 76.5363, "timezone": "Asia/Kolkata", "admin1": "Himachal Pradesh", "country": "India"},
    {"name": "Pharbhani", "latitude": 19.2608, "longitude": 76.7748, "timezone": "Asia/Kolkata", "admin1": "Maharashtra", "country": "India"},
    {"name": "Raipur", "latitude": 21.2514, "longitude": 81.6296, "timezone": "Asia/Kolkata", "admin1": "Chhattisgarh", "country": "India"},
    {"name": "Rajendranagar", "latitude": 17.3197, "longitude": 78.4069, "timezone": "Asia/Kolkata", "admin1": "Telangana", "country": "India"},
    {"name": "Sirsa", "latitude": 29.5349, "longitude": 75.0290, "timezone": "Asia/Kolkata", "admin1": "Haryana", "country": "India"},
]


def _load_supported_location_coords():
    global _SUPPORTED_LOCATION_COORDS
    if _SUPPORTED_LOCATION_COORDS is not None:
        return _SUPPORTED_LOCATION_COORDS

    _SUPPORTED_LOCATION_COORDS = STATIC_LOCATION_COORDS
    return _SUPPORTED_LOCATION_COORDS



def _nearest_supported_location(latitude: float, longitude: float):
    candidates = _load_supported_location_coords()
    if not candidates:
        return {
            "name": "Current location",
            "timezone": "auto",
            "admin1": None,
            "country": None,
        }

    return min(
        candidates,
        key=lambda item: _haversine_km(
            latitude,
            longitude,
            item["latitude"],
            item["longitude"],
        ),
    )


def reverse_geocode(latitude: float, longitude: float) -> dict | None:
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {"User-Agent": "AgriShield-AI/1.0 (agrishield@local)"}
        resp = requests.get(
            url,
            params={"lat": latitude, "lon": longitude, "format": "json"},
            headers=headers,
            timeout=4,
        )
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("address", {})
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("suburb")
                or address.get("county")
                or address.get("state_district")
            )
            state = address.get("state")
            country = address.get("country")
            short_name = f"{city}, {state}" if (city and state) else (city or state or data.get("name"))
            return {
                "name": short_name or f"{latitude:.2f}°N, {longitude:.2f}°E",
                "admin1": state,
                "country": country,
                "display_name": data.get("display_name"),
            }
    except Exception:
        pass
    return None


def search_locations(query: str, limit: int = 5) -> list[dict]:
    if not query or len(query.strip()) < 2:
        return []
    try:
        payload = _request_json(
            GEOCODING_URL,
            {
                "name": query.strip(),
                "count": limit,
                "language": "en",
                "format": "json",
            },
        )
        results = payload.get("results") or []
        formatted = []
        for r in results:
            name = r.get("name", "")
            admin1 = r.get("admin1")
            country = r.get("country")
            label_parts = [p for p in [name, admin1, country] if p]
            formatted.append({
                "name": name,
                "display_name": ", ".join(label_parts),
                "latitude": r.get("latitude"),
                "longitude": r.get("longitude"),
                "admin1": admin1,
                "country": country,
                "timezone": r.get("timezone", "auto"),
            })
        return formatted
    except Exception:
        return []


def geocode_location(location: str):
    payload = _request_json(
        GEOCODING_URL,
        {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )

    results = payload.get("results") or []
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find weather data for '{location}'. Try a more specific place name.",
        )

    return results[0]


def get_weather_snapshot(location: str):
    place = geocode_location(location)
    return get_weather_snapshot_by_coordinates(
        place["latitude"],
        place["longitude"],
        place.get("timezone") or "auto",
        location_label=place.get("name"),
        admin1=place.get("admin1"),
        country=place.get("country"),
    )


def get_weather_snapshot_by_coordinates(
    latitude: float,
    longitude: float,
    timezone_name: str = "auto",
    location_label: str | None = None,
    admin1: str | None = None,
    country: str | None = None,
):
    matched_location = _nearest_supported_location(latitude, longitude)
    if not location_label:
        rev = reverse_geocode(latitude, longitude)
        if rev and rev.get("name"):
            display_name = rev["name"]
            admin1 = admin1 or rev.get("admin1")
            country = country or rev.get("country")
        else:
            display_name = f"{latitude:.2f}°N, {longitude:.2f}°E ({matched_location['name']} Station)"
    else:
        display_name = location_label
    resolved_timezone = (
        timezone_name
        if timezone_name and timezone_name != "auto"
        else matched_location.get("timezone")
    )

    forecast = _request_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": resolved_timezone or "auto",
            "forecast_days": 1,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "precipitation",
                ]
            ),
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "sunshine_duration",
                    "et0_fao_evapotranspiration",
                    "wind_speed_10m_max",
                ]
            ),
        },
    )

    daily = forecast.get("daily", {})
    hourly = forecast.get("hourly", {})

    max_t = (daily.get("temperature_2m_max") or [None])[0]
    min_t = (daily.get("temperature_2m_min") or [None])[0]
    rainfall = (daily.get("precipitation_sum") or [None])[0]
    sunshine_duration = (daily.get("sunshine_duration") or [None])[0]
    evapotranspiration = (daily.get("et0_fao_evapotranspiration") or [None])[0]

    humidity_morning = _pick_hour_value(
        hourly.get("time") or [],
        hourly.get("relative_humidity_2m") or [],
        9,
    )
    humidity_evening = _pick_hour_value(
        hourly.get("time") or [],
        hourly.get("relative_humidity_2m") or [],
        18,
    )

    wind_speed_hourly = hourly.get("wind_speed_10m") or []
    wind_speed = float(sum(wind_speed_hourly) / len(wind_speed_hourly)) if wind_speed_hourly else None

    observation_year, standard_week = _current_year_week(resolved_timezone)

    return {
        "location": {
            "name": display_name,
            "admin1": admin1 or matched_location.get("admin1"),
            "country": country or matched_location.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": resolved_timezone or "auto",
        },
        "suggested_values": {
            "Observation_Year": observation_year,
            "Standard_Week": standard_week,
        },
        "weather": {
            "MaxT": max_t,
            "MinT": min_t,
            "RH1": humidity_morning,
            "RH2": humidity_evening,
            "RF": rainfall,
            "WS": wind_speed,
            "SSH": sunshine_duration / 3600 if sunshine_duration is not None else None,
            "EVP": evapotranspiration,
        },
        "source": "Open-Meteo",
    }


def get_current_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "precipitation",
            ]
        ),
    }

    response = requests.get(FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()

    current = response.json()["current"]

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "rainfall": current["precipitation"],
    }


def get_forecast_7days(
    latitude: float,
    longitude: float,
    timezone_name: str = "auto",
    location_label: str | None = None,
):
    """
    Fetches 7-day weather forecast formatted with all 8 features needed for ML risk prediction.
    """
    matched_location = _nearest_supported_location(latitude, longitude)
    if not location_label:
        rev = reverse_geocode(latitude, longitude)
        display_name = rev["name"] if (rev and rev.get("name")) else f"{latitude:.2f}°N, {longitude:.2f}°E"
    else:
        display_name = location_label
    resolved_timezone = (
        timezone_name
        if timezone_name and timezone_name != "auto"
        else matched_location.get("timezone") or "auto"
    )

    forecast = _request_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": resolved_timezone,
            "forecast_days": 7,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "precipitation",
                ]
            ),
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "sunshine_duration",
                    "et0_fao_evapotranspiration",
                    "wind_speed_10m_max",
                ]
            ),
        },
    )

    daily = forecast.get("daily", {})
    hourly = forecast.get("hourly", {})

    dates = daily.get("time") or []
    max_temps = daily.get("temperature_2m_max") or []
    min_temps = daily.get("temperature_2m_min") or []
    rainfalls = daily.get("precipitation_sum") or []
    sunshines = daily.get("sunshine_duration") or []
    evapotranspirations = daily.get("et0_fao_evapotranspiration") or []
    wind_maxs = daily.get("wind_speed_10m_max") or []

    hourly_times = hourly.get("time") or []
    hourly_humidities = hourly.get("relative_humidity_2m") or []
    hourly_winds = hourly.get("wind_speed_10m") or []

    forecast_list = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i, date_str in enumerate(dates):
        try:
            dt = datetime.fromisoformat(date_str)
            day_name = day_names[dt.weekday()]
            obs_year = dt.year
            std_week = int(dt.isocalendar().week)
        except Exception:
            day_name = f"Day {i+1}"
            obs_year = 2026
            std_week = 35

        # Extract 9am and 6pm humidity for this specific date
        day_hourly_hum = []
        day_hourly_wind = []
        for t_stamp, hum, w_spd in zip(hourly_times, hourly_humidities, hourly_winds):
            if t_stamp.startswith(date_str):
                day_hourly_hum.append((t_stamp, hum))
                day_hourly_wind.append(w_spd)

        rh1 = 75.0
        rh2 = 55.0
        if day_hourly_hum:
            for t_stamp, hum in day_hourly_hum:
                hr = int(t_stamp[11:13])
                if hr == 9:
                    rh1 = float(hum)
                elif hr == 18:
                    rh2 = float(hum)

        ws = (
            float(sum(day_hourly_wind) / len(day_hourly_wind))
            if day_hourly_wind
            else (float(wind_maxs[i]) if i < len(wind_maxs) and wind_maxs[i] is not None else 5.0)
        )

        max_t = float(max_temps[i]) if i < len(max_temps) and max_temps[i] is not None else 32.0
        min_t = float(min_temps[i]) if i < len(min_temps) and min_temps[i] is not None else 24.0
        rf = float(rainfalls[i]) if i < len(rainfalls) and rainfalls[i] is not None else 0.0
        ssh_raw = sunshines[i] if i < len(sunshines) else None
        ssh = round(ssh_raw / 3600.0, 1) if ssh_raw is not None else 7.0
        evp_raw = evapotranspirations[i] if i < len(evapotranspirations) else None
        evp = round(float(evp_raw), 2) if evp_raw is not None else 4.0

        forecast_list.append({
            "date": date_str,
            "day_name": day_name,
            "Observation_Year": obs_year,
            "Standard_Week": std_week,
            "MaxT": round(max_t, 1),
            "MinT": round(min_t, 1),
            "RH1": round(rh1, 1),
            "RH2": round(rh2, 1),
            "RF": round(rf, 1),
            "WS": round(ws, 1),
            "SSH": ssh,
            "EVP": evp,
        })

    return {
        "location": {
            "name": display_name,
            "matched_training_location": matched_location["name"],
            "latitude": latitude,
            "longitude": longitude,
            "timezone": resolved_timezone,
        },
        "days": forecast_list,
    }

