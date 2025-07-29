from __future__ import annotations

import requests

from mooch.location.exceptions import LocationError
from mooch.location.state_abbrev import abbrev_to_state, state_to_abbrev, valid_state, valid_state_abbrev


class Location:
    def __init__(self, zip_code: int | None = None, city: str | None = None, state: str | None = None) -> None:
        """Initialize a Location instance with the specified zip code or city/state.

        Args:
            zip_code (int): The zip code to associate with this location.
            city (str): The city name to associate with this location.
            state (str): The state name to associate with this location.

        """
        if zip_code is not None and (city is not None or state is not None):
            msg = "Provide either `zip_code` OR `city` and `state`, but not both."
            raise ValueError(msg)

        if zip_code is None and (city is None or state is None):
            msg = "You must provide either a `zip_code` OR both `city` and `state`."
            raise ValueError(msg)

        self.zip_code = zip_code
        self.city = city
        self.state = state
        self.state_abbreviation = None
        self.latitude = None
        self.longitude = None

        if self.zip_code is not None:
            self._load_from_zip_code()

        if city is not None:
            self._load_from_city_and_state()

    def _load_from_zip_code(self) -> None:
        """Load and populate the location data (city, state, state abbr., lat, long) from the Zippopotam.us API."""
        url = f"https://api.zippopotam.us/us/{self.zip_code}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:  # noqa: PLR2004
            message = f"Invalid zip code {self.zip_code}."
            raise LocationError(message)

        data = res.json()
        self.city = data["places"][0]["place name"]
        self.state = data["places"][0]["state"]
        self.state_abbreviation = data["places"][0]["state abbreviation"]
        self.latitude = float(data["places"][0]["latitude"])
        self.longitude = float(data["places"][0]["longitude"])

    def _load_from_city_and_state(self) -> None:
        """Load and populate the location data (zipcode, lat, long) from the Zippopotam.us API."""
        if valid_state_abbrev(self.state):
            self.state_abbreviation = self.state
            self.state = abbrev_to_state(self.state)
        elif valid_state(self.state):
            self.state_abbreviation = state_to_abbrev(self.state)
            self.state = self.state.strip().title()
        else:
            message = f"Invalid state name or abbreviation: {self.state}."
            raise LocationError(message)

        url = f"https://api.zippopotam.us/us/{self.state_abbreviation}/{self.city}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:  # noqa: PLR2004
            message = f"Invalid city/state combination: {self.city}, {self.state}."
            raise LocationError(message)

        data = res.json()
        self.zip_code = int(data["places"][0]["post code"])
        self.latitude = float(data["places"][0]["latitude"])
        self.longitude = float(data["places"][0]["longitude"])
