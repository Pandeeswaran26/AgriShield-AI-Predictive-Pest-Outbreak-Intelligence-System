from fastapi import APIRouter, Query

from .service import (
    get_current_weather,
    get_weather_snapshot,
    get_weather_snapshot_by_coordinates,
    get_forecast_7days,
    search_locations,
)

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/search")
def search_places(query: str = Query(..., min_length=2)):
    return search_locations(query)


@router.get("/current")
def current_weather(lat: float, lon: float):
    return get_current_weather(lat, lon)


@router.get("/location")
def location_weather(location: str = Query(..., min_length=2)):
    return get_weather_snapshot(location)


@router.get("/coordinates")
def coordinates_weather(lat: float, lon: float):
    return get_weather_snapshot_by_coordinates(lat, lon)


@router.get("/forecast")
def forecast_weather(lat: float, lon: float):
    return get_forecast_7days(lat, lon)
