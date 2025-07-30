from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.blank_node import group_by_keys
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.lookup import _node_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{
            "@type": "Indicator",
            "value": "",
            "term.@id": [
                "ionisingCompoundsToAirInputsProduction",
                "ionisingCompoundsToWaterInputsProduction",
                "ionisingCompoundsToSaltwaterInputsProduction"
            ],
            "inputs": [{"@type": "Term", "term.termType": "waste", "term.units": "kg"}]
        }]
    }
}
LOOKUPS = {
    "waste": [
        "ionisingCompoundsToAirInputsProduction",
        "ionisingCompoundsToWaterInputsProduction",
        "ionisingCompoundsToSaltwaterInputsProduction"
    ]
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "inputs": ""
    }]
}

TERM_ID = 'ionisingRadiationKbqU235Eq'


def _valid_waste(input: dict) -> bool:
    return input.get('units', '').startswith("kg") and input.get('termType', '') == TermTermType.WASTE.value


def _valid_emission(emission: dict) -> bool:
    return len(emission.get('inputs', [])) == 1 and isinstance(_node_value(emission), (int, float))


def _indicator(value: float, input: dict) -> dict:
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['inputs'] = [input]
    return indicator


def _run(emissions: list) -> list[dict]:
    indicators = [
        _indicator(value=list_sum([emission['value'] * emission['coefficient'] for emission in emission_group]),
                   input=emission_group[0]['input'])
        for emission_group in reduce(group_by_keys(['input']), emissions, {}).values()
    ]

    return indicators


def _should_run(impact_assessment: dict) -> tuple[bool, list]:
    emissions = [
        emission
        for emission in filter_list_term_type(impact_assessment.get('emissionsResourceUse', []), TermTermType.EMISSION)
        if emission.get('term', {}).get('@id', '') in LOOKUPS[TermTermType.WASTE.value]
    ]

    has_emissions = bool(emissions)

    emissions_unpacked = flatten(
        [
            [
                {
                    "input-term-id": input.get('@id'),
                    "input-term-type": input.get('termType'),
                    "indicator-term-id": emission['term']['@id'],
                    "indicator-is-valid": _valid_emission(emission),
                    "input": input,
                    "indicator-input-is-valid": _valid_waste(input),
                    "value": _node_value(emission),
                    "coefficient": get_table_value(lookup=download_lookup(filename="waste.csv"),
                                                   col_match='termid',
                                                   col_match_with=input.get('@id'),
                                                   col_val=column_name(emission['term']['@id'])) if input else None
                } for input in emission['inputs'] or [{}]]
            for emission in emissions
        ]
    )

    valid_emission_with_cf = [
        em for em in emissions_unpacked if all([
            em['coefficient'] is not None,
            em['indicator-is-valid'] is True,
            em['indicator-input-is-valid'] is True
        ])
    ]

    valid_input_requirements = all([
        all([
            em['indicator-is-valid'],
            em['indicator-input-is-valid']
        ])
        for em in emissions_unpacked
    ])

    all_emissions_have_known_cf = all([
        em['coefficient'] is not None for em in emissions_unpacked
    ]) and bool(emissions_unpacked)

    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    has_emissions=has_emissions,
                    valid_input_requirements=valid_input_requirements,
                    all_emissions_have_known_CF=all_emissions_have_known_cf,
                    emissions=log_as_table(emissions_unpacked)
                    )

    should_run = valid_input_requirements

    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run, valid_emission_with_cf


def run(impact_assessment: dict):
    should_run, emissions = _should_run(impact_assessment)
    return _run(emissions) if should_run else []
