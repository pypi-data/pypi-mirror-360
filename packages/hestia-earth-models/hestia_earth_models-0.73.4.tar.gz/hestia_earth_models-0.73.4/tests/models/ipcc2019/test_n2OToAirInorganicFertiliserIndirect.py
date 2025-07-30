from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.n2OToAirInorganicFertiliserIndirect import (
    MODEL, TERM_ID, run, _should_run, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    # no emissions => no run
    cycle = {'completeness': {'fertiliser': True}, 'emissions': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with no3 emission => run
    cycle['emissions'] = [
        {
            'term': {'@id': NO3_TERM_ID},
            'value': [100]
        },
        {
            'term': {'@id': NH3_TERM_ID},
            'value': [100]
        },
        {
            'term': {'@id': NOX_TERM_ID},
            'value': [100]
        }
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_wet(*args):
    with open(f"{fixtures_folder}/ecoClimateZone-wet/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/ecoClimateZone-wet/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_dry(*args):
    with open(f"{fixtures_folder}/ecoClimateZone-dry/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/ecoClimateZone-dry/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
