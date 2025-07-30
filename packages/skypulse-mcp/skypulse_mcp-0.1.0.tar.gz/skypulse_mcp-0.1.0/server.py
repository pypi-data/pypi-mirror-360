from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("weather-mcp")

OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
USER_AGENT = "weather-app"


async def make_openmeteo_request(url: str) -> str | None:
    """Make a request to the Open-Meteo API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """
    Get the current weather for a given latitude and longitude.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """

    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,snowfall,precipitation,relative_humidity_2m,apparent_temperature,rain,weather_code,surface_pressure,wind_gusts_10m"

    response = await make_openmeteo_request(url)
    if not response:
        return "Unable to get weather data."
    
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_forecast_for_days(latitude: float, longitude: float, days: int) -> str:
    """
    Get the forecast for a given latitude and longitude for a given number of days.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        days: The number of days to forecast.
    """
    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,rain_sum,snowfall_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant&timezone=auto&forecast_days={days}"
    response = await make_openmeteo_request(url)
    if not response:
        return "Unable to get forecast data."
    
    return json.dumps(response, indent=2)


if __name__ == "__main__":
    mcp.run()
