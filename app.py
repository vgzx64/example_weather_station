"""A minimal weather API.

Serves randomly generated weather information and strictly supports only two
cities: **Astana** and **Almaty**. Any other city name responds with
``404 Not Found``.

Run locally with::

    uv run uvicorn app:app --reload
"""
from __future__ import annotations

import random
from typing import Final

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Weather API", version="1.0.0")

# The only cities this service is allowed to report weather for.
SUPPORTED_CITIES: Final[set[str]] = {"Astana", "Almaty"}

# A small vocabulary of weather conditions to pick from at random.
_CONDITIONS: Final[tuple[str, ...]] = (
    "Sunny",
    "Partly Cloudy",
    "Cloudy",
    "Rainy",
    "Snowy",
    "Windy",
)


class WeatherResponse(BaseModel):
    """The weather report returned to clients."""

    city: str
    temperature: float
    feels_like: float
    condition: str
    humidity: int
    wind_speed: float


def _generate_weather(city: str) -> WeatherResponse:
    """Build a random :class:`WeatherResponse` for *city*."""
    temperature = round(random.uniform(-35.0, 40.0), 1)
    feels_like = round(temperature + random.uniform(-3.0, 3.0), 1)
    return WeatherResponse(
        city=city,
        temperature=temperature,
        feels_like=feels_like,
        condition=random.choice(_CONDITIONS),
        humidity=random.randint(15, 100),
        wind_speed=round(random.uniform(0.0, 20.0), 1),
    )


@app.get("/")
def read_root() -> dict[str, object]:
    """Service information and the list of supported cities."""
    return {
        "service": "Example Weather API",
        "supported_cities": sorted(SUPPORTED_CITIES),
    }


@app.get("/weather/{city}", response_model=WeatherResponse)
def get_weather(city: str) -> WeatherResponse:
    """Return random weather for a supported *city*.

    Only ``Astana`` and ``Almaty`` are accepted; anything else raises 404.
    """
    if city not in SUPPORTED_CITIES:
        raise HTTPException(
            status_code=404,
            detail=(
                f"City '{city}' is not supported. "
                f"Supported cities: {sorted(SUPPORTED_CITIES)}"
            ),
        )
    return _generate_weather(city)


def main() -> None:
    """Entry point used by ``python -m app`` and the ``example2`` script."""
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
