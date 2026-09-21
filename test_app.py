"""Tests for the weather API."""
from __future__ import annotations

import random

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import (
    SUPPORTED_CITIES,
    WeatherResponse,
    _CONDITIONS,
    app,
)


@pytest.fixture
def client() -> TestClient:
    """A synchronous test client for the FastAPI app."""
    return TestClient(app)


def test_root_lists_supported_cities(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["service"] == "Weather API"
    assert set(body["supported_cities"]) == SUPPORTED_CITIES


@pytest.mark.parametrize("city", ["Astana", "Almaty"])
def test_weather_for_supported_city(client: TestClient, city: str) -> None:
    response = client.get(f"/weather/{city}")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["city"] == city
    # Values are random, but always stay within sensible bounds.
    assert -40.0 <= body["temperature"] <= 40.0
    assert -45.0 <= body["feels_like"] <= 45.0
    assert body["condition"] in _CONDITIONS
    assert 15 <= body["humidity"] <= 100
    assert 0.0 <= body["wind_speed"] <= 20.0


def test_weather_response_matches_model_schema(client: TestClient) -> None:
    response = client.get("/weather/Astana")
    assert response.status_code == status.HTTP_200_OK
    # Validates the payload against the Pydantic model (types + fields).
    WeatherResponse.model_validate(response.json())


def test_unsupported_city_returns_404(client: TestClient) -> None:
    response = client.get("/weather/London")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not supported" in response.json()["detail"].lower()


@pytest.mark.parametrize("bad_city", ["astana", "ALMATY", "Moskva", "Almaty1"])
def test_only_exact_city_names_are_accepted(client: TestClient, bad_city: str) -> None:
    """The service strictly allows only the two canonical city names."""
    response = client.get(f"/weather/{bad_city}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_weather_is_random(client: TestClient) -> None:
    """Successive calls should not always return the same temperature."""
    temperatures = {
        client.get("/weather/Astana").json()["temperature"] for _ in range(30)
    }
    assert len(temperatures) > 1


def test_weather_is_deterministic_under_controlled_seed(client: TestClient) -> None:
    """With a fixed RNG seed the generated weather is reproducible."""
    random.seed(123)
    first = client.get("/weather/Almaty").json()
    random.seed(123)
    second = client.get("/weather/Almaty").json()
    assert first == second
