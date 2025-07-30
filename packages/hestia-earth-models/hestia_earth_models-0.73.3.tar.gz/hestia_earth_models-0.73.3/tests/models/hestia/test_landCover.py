import os
import json
import pytest
from unittest.mock import patch

from tests.utils import fixtures_path, fake_new_management
from hestia_earth.models.faostat2018.utils import MODEL as FAOSTAT_MODEL
from hestia_earth.models.hestia.landCover import (
    MODEL, MODEL_KEY, _get_changes, _estimate_maximum_forest_change,
    run, site_area_sum_to_100, _get_sums_of_crop_expansion, _get_sum_for_land_category, scale_values_to_one,
    _get_most_common_or_alphabetically_first
)

CLASS_PATH = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"
_folders = [d for d in os.listdir(fixtures_folder) if os.path.isdir(os.path.join(fixtures_folder, d))]

FAOSTAT_CLASS_PATH = f"hestia_earth.models.{FAOSTAT_MODEL}.utils"
faostat_fixtures_folder = f"{fixtures_path}/{FAOSTAT_MODEL}/utils"

BRAZIL_SITE = {
    "@type": "Site",
    "id": "Brazil-example",
    "country": {
        "name": "Brazil",
        "type": "Term"
    },
    "siteType": "cropland",
    "management": [
        {
            "term": {
                "@id": "maizePlant",
                "name": "Maize plant",
                "type": "Term",
                "termType": "landCover"
            },
            "value": 100,
            "startDate": "2010-01-01",
            "endDate": "2010-12-31",
            "type": "Management"
        }
    ]
}


@pytest.mark.parametrize(
    "terms,expected_output",
    [
        (   # Only term
            ["Annual crops", "Annual crops"],
            "Annual crops"
        ),
        (  # Most common
            ["Perennial crops", "Perennial crops", "Annual crops"],
            "Perennial crops"
        ),
        (   # Tied frequency, Alphabetically first
            ["Perennial crops", "Perennial crops", "Annual crops", "Annual crops"],
            "Annual crops"
        )
    ]
)
def test_get_most_common_or_alphabetically_first(terms, expected_output):
    actual_result = _get_most_common_or_alphabetically_first(terms)
    assert actual_result == expected_output


def test_get_changes():
    result, missing_values = _get_changes(
        country_id="GADM-AFG",
        end_year=2010
    )
    assert (
        result == {
            "Arable land": -117.0,
            "Cropland": -123.0,
            "Forest land": 0,
            "Other land": 123.0,
            "Land area": 0,
            "Permanent crops": -6.0,
            "Permanent meadows and pastures": 0,
            "Total agricultural change": -123.0
        }
    )


@pytest.mark.parametrize(
    "description,inputs,expected_output",
    [
        (
            "Annual cropland gain from forest",
            {
                "forest_change": -1000,
                "total_cropland_change": 1000,
                "pasture_change": 0,
                "total_agricultural_change": 1000
            },
            -1000
        ),
        (
            "Pasture gain from forest",
            {
                "forest_change": -1000,
                "total_cropland_change": 0,
                "pasture_change": 1000,
                "total_agricultural_change": 1000
            },
            -1000
        ),
        (
            "Brazil",
            {
                "forest_change": -77317,
                "total_cropland_change": 5201,
                "pasture_change": -8267,
                "total_agricultural_change": -3066
            },
            -5201
        ),
        (
            "Argentina",
            {
                "forest_change": -4990,
                "total_cropland_change": 11408,
                "pasture_change": -12705,
                "total_agricultural_change": -1297
            },
            -4990
        ),
        (
            "Madagascar",
            {
                "forest_change": -1131,
                "total_cropland_change": 275,
                "pasture_change": 4295,
                "total_agricultural_change": 4570
            },
            -1131
        ),
        (
            "Afforestation",
            {
                "forest_change": 100,
                "total_cropland_change": -1000,
                "pasture_change": -50,
                "total_agricultural_change": -1000
            },
            0
        ),
        (
            "Pasture gain more than forest loss",
            {
                "forest_change": -49,
                "total_cropland_change": -1000,
                "pasture_change": 50,
                "total_agricultural_change": -950
            },
            -49
        )
    ]
)
def test_estimate_maximum_forest_change(description, inputs, expected_output):
    assert _estimate_maximum_forest_change(**inputs) == expected_output, description


@pytest.mark.parametrize(
    "description,inputs,expected_result",
    [
        ("All zeros, OK", {"a": 0, "b": 0, "c": 0.0, "d": 0.0}, True),
        ("Exactly 1, OK", {"a": 0.1, "b": 0.5, "c": 0.4, "d": 0.0}, True),
        ("Almost 1, OK", {"a": 0.1, "b": 0.5, "c": 0.4, "d": 0.01}, True),
        ("Less than 1, Fail", {"a": 0.1, "b": 0, "c": 0.0, "d": 0.65}, False),
        ("More than 1, Fail", {"a": 0.15, "b": 0.7, "c": 0.0, "d": 0.65}, False),
    ]
)
def test_check_sum_of_percentages(description, inputs, expected_result):
    assert site_area_sum_to_100(dict_of_percentages=inputs) == expected_result


def test_get_sums_of_crop_expansion():
    result = _get_sums_of_crop_expansion(
        country_id="GADM-AFG",
        year=2010,
        include_negatives=True
    )
    assert result == (753973.3, 18354.0)

    result = _get_sums_of_crop_expansion(
        country_id="GADM-AFG",
        year=2010,
        include_negatives=False
    )
    assert result == (940270.0, 28139.0)


def test_get_sum_for_land_category():
    values = {
        "mangoes_guavas_and_mangosteens": "2022:5",
        "kiwi_fruit": "2020:4",
        "maize_corn": "2020:3",
        "other_beans_green": "2021:2",
        "olives": "2020:-1"
    }
    fao_stat_to_ipcc_type = {
            "mangoes_guavas_and_mangosteens": "Perennial crops",
            'kiwi_fruit': "Perennial crops",
            'maize_corn': "Annual crops",
            'other_beans_green': "Annual crops",
            'olives': "Perennial crops"
    }
    result = _get_sum_for_land_category(
        values=values,
        year=2020,
        ipcc_land_use_category="Perennial crops",
        fao_stat_to_ipcc_type=fao_stat_to_ipcc_type,
        include_negatives=True
    )
    assert result == 3.0


@pytest.mark.parametrize(
    "dictionary,expected_result",
    [
        (
            {"a": 0, "b": 0, "c": 0},
            {"a": 0, "b": 0, "c": 0}
        ),
        (
            {"a": 1000},
            {"a": 1}
        ),
        (
            {"a": 10, "b": 5, "c": 3},
            {"a": 0.5556, "b": 0.2778, "c": 0.1667}
        )
    ]
)
def test_scale_values_to_one(dictionary, expected_result):
    result = scale_values_to_one(dictionary)
    for k, v in result.items():
        assert k in expected_result
        assert round(v, 3) == round(expected_result[k], 3)


@pytest.mark.parametrize("subfolder", _folders)
@patch(f"{CLASS_PATH}._new_management", side_effect=fake_new_management)
def test_run(mock, subfolder: str):
    folder = f"{fixtures_folder}/{subfolder}"
    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
