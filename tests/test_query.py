import pytest
from unittest.mock import patch

from tests.utils import (
    extract_tags_from_ntee,
    parse_location,
    filter_fields,
    get_filtered_charities
)

MOCK_NTEE_CODES = [
    "P84: Ethnic, Immigrant Centers, Services",
    "Q71: International Migration, Refugee Issues"
]

MOCK_CHARITY = {
    "charityName": "Test Charity",
    "ein": "123456789",
    "category": "Human Services",
    "url": "http://example.com/org/123456789",
    "website": "http://test.org",
    "missionStatement": "Helping immigrants and refugees.",
    "acceptingDonations": 1,
    "score": 5
}


def test_extract_tags_from_ntee():
    tags = extract_tags_from_ntee(MOCK_NTEE_CODES)
    assert tags == [
        "Ethnic", "Immigrant Centers", "Services",
        "International Migration", "Refugee Issues"
    ]


def test_parse_location():
    city, state = parse_location("Los Angeles, CA")
    assert city == "Los Angeles"
    assert state == "CA"

    city, state = parse_location("New York")
    assert city == "New York"
    assert state == ""


def test_filter_fields():
    fields = [
        "charityName", "ein", "category", "url",
        "website", "missionStatement", "acceptingDonations", "score"
    ]
    filtered = filter_fields([MOCK_CHARITY], fields)
    assert filtered == [{key: MOCK_CHARITY[key] for key in fields}]


@patch("cli.utils.get_top_rated_charities")
def test_get_filtered_charities(mock_api_call):
    mock_api_call.return_value = [MOCK_CHARITY]
    results = get_filtered_charities(["Immigrant Centers"], "Los Angeles", "CA")
    assert len(results) == 1
    assert results[0]["charityName"] == "Test Charity"
