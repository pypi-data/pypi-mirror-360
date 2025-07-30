from functools import reduce
from statistics import mean
from hestia_earth.schema import IndicatorMethodTier
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import debugValues, logShouldRun, logRequirements
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.background_emissions import get_background_inputs
from hestia_earth.models.utils.blank_node import group_by_keys
from .utils import get_input_mappings, ecoalim_values
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "inputs": [{
                "@type": "Input",
                "value": "> 0",
                "none": {
                    "fromCycle": "True",
                    "producedInCycle": "True"
                }
            }],
            "optional": {
                "animals": [{
                    "@type": "Animal",
                    "inputs": [{
                        "@type": "Input",
                        "value": "> 0",
                        "none": {
                            "fromCycle": "True",
                            "producedInCycle": "True"
                        }
                    }]
                }]
            }
        }
    }
}
RETURNS = {
    "Indicator": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": ""
    }]
}
LOOKUPS = {
    "ecoalim-emissionsResourceUse": "resourceUse-",
    "crop": "ecoalimMapping",
    "processedFood": "ecoalimMapping",
    "animalProduct": "ecoalimMapping",
    "forage": "ecoalimMapping",
    "feedFoodAdditive": "ecoalimMapping"
}
MODEL_KEY = 'impact_assessment'
TIER = IndicatorMethodTier.BACKGROUND.value


def _indicator(term_id: str, value: float, input: dict):
    indicator = _new_indicator(term_id, MODEL)
    indicator['value'] = value
    indicator['methodTier'] = TIER
    indicator['inputs'] = [input.get('term')]
    if input.get('operation'):
        indicator['operation'] = input.get('operation')
    return indicator


def _add_indicator(cycle: dict, input: dict):
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('@id')
    animal_term_id = input.get('animal', {}).get('@id')

    def add(prev: dict, mapping: tuple):
        gadm_id, ecoalim_key = mapping
        # all countries have the same coefficient
        coefficient = 1
        indicators = ecoalim_values(ecoalim_key, 'resourceUse')
        for indicator_term_id, value in indicators:
            # log run on each indicator so we know it did run
            logShouldRun(cycle, MODEL, input_term_id, True, methodTier=TIER, emission_id=indicator_term_id)
            debugValues(cycle, model=MODEL, term=indicator_term_id, model_key=MODEL_KEY,
                        value=value,
                        coefficient=coefficient,
                        input=input_term_id,
                        operation=operation_term_id,
                        animal=animal_term_id)
            if value is not None:
                prev[indicator_term_id] = prev.get(indicator_term_id, []) + [value * coefficient]
        return prev
    return add


def _run_input(impact_assessment: dict):
    def run(inputs: list):
        input = inputs[0]
        input_term_id = input.get('term', {}).get('@id')
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        mappings = get_input_mappings(MODEL, input)
        has_mappings = len(mappings) > 0

        logRequirements(impact_assessment, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        has_ecoalim_mappings=has_mappings,
                        ecoalim_mappings=';'.join([v[1] for v in mappings]),
                        input_value=input_value)

        should_run = all([has_mappings, input_value])
        logShouldRun(
            impact_assessment, MODEL, input_term_id, should_run, methodTier=TIER, model_key=MODEL_KEY
        )

        grouped_indicators = reduce(_add_indicator(impact_assessment, input), mappings, {}) if should_run else {}
        return [
            _indicator(term_id, mean(value) * input_value, input)
            for term_id, value in grouped_indicators.items()
        ]
    return run


def run(impact_assessment: dict):
    inputs = get_background_inputs(impact_assessment.get('cycle', {}))
    grouped_inputs = reduce(group_by_keys(['term', 'operation']), inputs, {})
    return flatten(map(_run_input(impact_assessment), grouped_inputs.values()))
