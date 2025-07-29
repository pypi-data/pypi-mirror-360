import pytest

from mooch.location import state_abbrev


def test_valid_state_true():
    assert state_abbrev.valid_state("California")
    assert state_abbrev.valid_state("  texas ")
    assert state_abbrev.valid_state("new york")
    assert state_abbrev.valid_state("Alabama")


def test_valid_state_false():
    assert not state_abbrev.valid_state("Californias")
    assert not state_abbrev.valid_state("Cali")
    assert not state_abbrev.valid_state("")
    assert not state_abbrev.valid_state(" ")


def test_valid_state_abbrev_true():
    assert state_abbrev.valid_state_abbrev("CA")
    assert state_abbrev.valid_state_abbrev("ny")
    assert state_abbrev.valid_state_abbrev(" tx ")
    assert state_abbrev.valid_state_abbrev("FL")


def test_valid_state_abbrev_false():
    assert not state_abbrev.valid_state_abbrev("C")
    assert not state_abbrev.valid_state_abbrev("CALI")
    assert not state_abbrev.valid_state_abbrev("")
    assert not state_abbrev.valid_state_abbrev("ZZ")


def test_state_to_abbrev_success():
    assert state_abbrev.state_to_abbrev("California") == "CA"
    assert state_abbrev.state_to_abbrev("texas") == "TX"
    assert state_abbrev.state_to_abbrev(" new york ") == "NY"
    assert state_abbrev.state_to_abbrev("Alabama") == "AL"


def test_state_to_abbrev_invalid():
    with pytest.raises(ValueError):
        state_abbrev.state_to_abbrev("Californias")
    with pytest.raises(ValueError):
        state_abbrev.state_to_abbrev("")
    with pytest.raises(ValueError):
        state_abbrev.state_to_abbrev("Cali")


def test_abbrev_to_state_success():
    assert state_abbrev.abbrev_to_state("CA") == "California"
    assert state_abbrev.abbrev_to_state("ny") == "New York"
    assert state_abbrev.abbrev_to_state(" tx ") == "Texas"
    assert state_abbrev.abbrev_to_state("AL") == "Alabama"


def test_abbrev_to_state_invalid():
    with pytest.raises(ValueError):
        state_abbrev.abbrev_to_state("CALI")
    with pytest.raises(ValueError):
        state_abbrev.abbrev_to_state("")
    with pytest.raises(ValueError):
        state_abbrev.abbrev_to_state("ZZ")
