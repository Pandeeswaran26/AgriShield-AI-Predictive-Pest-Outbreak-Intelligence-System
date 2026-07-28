from fastapi import APIRouter
from .service import get_current_weather

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/current")
def current_weather(lat: float, lon: float):
    return get_current_weather(lat, lon)