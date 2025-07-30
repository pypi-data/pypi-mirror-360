import pytest
import requests

from mooch.location.exceptions import LocationError
from mooch.location.location import Location


def test_zip_to_city_state_success(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "country": "United States",
                "country abbreviation": "US",
                "post code": "62704",
                "places": [
                    {
                        "place name": "Springfield",
                        "longitude": "-89.6889",
                        "latitude": "39.7725",
                        "state": "Illinois",
                        "state abbreviation": "IL",
                    },
                ],
            }

    def mock_get(url, timeout):
        assert url == "https://api.zippopotam.us/us/62704"
        assert timeout == 5
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    location = Location(62704)
    assert location.city == "Springfield"
    assert location.state == "Illinois"
    assert location.state_abbreviation == "IL"
    assert location.latitude == 39.7725
    assert location.longitude == -89.6889


def test_zip_to_city_state_failure_status(monkeypatch):
    class MockResponse:
        status_code = 404

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(LocationError) as excinfo:
        location = Location(99999)
    assert "Invalid zip code 99999." in str(excinfo.value)


def test_zip_to_city_state_request_timeout(monkeypatch):
    def mock_get(url, timeout):
        raise requests.Timeout("Request timed out")

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(requests.Timeout):
        location = Location(90210)


def test_zip_code_required():
    with pytest.raises(ValueError) as excinfo:
        _ = Location()
    assert "provide either" in str(excinfo.value)


def test_location_init_with_city_and_state_success(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "country": "United States",
                "country abbreviation": "US",
                "state": "Illinois",
                "state abbreviation": "IL",
                "place name": "Springfield",
                "places": [
                    {
                        "place name": "Springfield",
                        "longitude": "-89.6495",
                        "latitude": "39.8",
                        "post code": "62701",
                    },
                ],
            }

    def mock_get(url, timeout):
        assert url == "https://api.zippopotam.us/us/IL/Springfield"
        assert timeout == 5
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    location = Location(city="Springfield", state="Illinois")
    assert location.city == "Springfield"
    assert location.state == "Illinois"
    assert location.state_abbreviation == "IL"
    assert location.latitude == 39.8
    assert location.longitude == -89.6495
    assert location.zip_code == 62701


def test_location_init_with_city_and_state_invalid_state(monkeypatch):
    class MockResponse:
        status_code = 404

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(LocationError) as excinfo:
        _ = Location(city="Springfield", state="InvalidState")
    assert "Invalid state name or abbreviation: InvalidState." in str(excinfo.value)


def test_location_init_with_city_and_state_valid_abbrev(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "country": "United States",
                "country abbreviation": "US",
                "state": "Illinois",
                "state abbreviation": "IL",
                "place name": "Springfield",
                "places": [
                    {
                        "place name": "Springfield",
                        "longitude": "-89.6495",
                        "latitude": "39.8",
                        "post code": "62701",
                    },
                ],
            }

    def mock_get(url, timeout):
        assert url == "https://api.zippopotam.us/us/IL/Springfield"
        assert timeout == 5
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    location = Location(city="Springfield", state="IL")
    assert location.city == "Springfield"
    assert location.state == "Illinois"
    assert location.state_abbreviation == "IL"
    assert location.latitude == 39.8
    assert location.longitude == -89.6495
    assert location.zip_code == 62701


def test_city_state_request_timeout(monkeypatch):
    def mock_get(url, timeout):
        raise requests.Timeout("Request timed out")

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(requests.Timeout):
        location = Location(city="Springfield", state="Illinois")


def test_city_state_failure_status(monkeypatch):
    class MockResponse:
        status_code = 404

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(LocationError) as excinfo:
        location = Location(city="Fake City", state="IL")
    assert "Invalid city/state combination" in str(excinfo.value)


def test_zip_and_city_but_not_state():
    with pytest.raises(ValueError) as excinfo:
        _ = Location(zip_code=62704, city="Springfield")
    assert "but not both" in str(excinfo.value)


def test_zip_and_state_but_not_city():
    with pytest.raises(ValueError) as excinfo:
        _ = Location(zip_code=62704, state="IL")
    assert "but not both" in str(excinfo.value)
