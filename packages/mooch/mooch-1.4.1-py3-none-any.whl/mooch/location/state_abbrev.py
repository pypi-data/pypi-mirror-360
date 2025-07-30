STATE_TO_ABBREV = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def valid_state(state: str) -> bool:
    """Check if the provided state name is valid."""
    state_clean = state.strip().title()
    return state_clean in STATE_TO_ABBREV


def valid_state_abbrev(abbrev: str) -> bool:
    """Check if the provided state abbreviation is valid."""
    abbrev_clean = abbrev.strip().upper()
    return abbrev_clean in STATE_TO_ABBREV.values()


def state_to_abbrev(state: str) -> str:
    """Convert a full U.S. state name to its two-letter abbreviation."""
    state_clean = state.strip().title()
    if not valid_state(state_clean):
        msg = f"Invalid state name: '{state}'"
        raise ValueError(msg)

    return STATE_TO_ABBREV.get(state_clean)


def abbrev_to_state(abbrev: str) -> str:
    """Convert a state abbreviation to its full name."""
    abbrev_clean = abbrev.strip().upper()
    if not valid_state_abbrev(abbrev_clean):
        msg = f"Invalid state abbreviation: '{abbrev}'"
        raise ValueError(msg)
    abbrev_to_state_dict = {v: k for k, v in STATE_TO_ABBREV.items()}
    return abbrev_to_state_dict.get(abbrev_clean)
