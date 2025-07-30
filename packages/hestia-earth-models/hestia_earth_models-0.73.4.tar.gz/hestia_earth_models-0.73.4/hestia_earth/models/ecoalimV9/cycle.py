from functools import reduce
from statistics import mean
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import debugValues, logShouldRun, logRequirements
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.background_emissions import get_background_inputs, no_gap_filled_background_emissions
from hestia_earth.models.utils.blank_node import group_by_keys
from .utils import get_input_mappings, ecoalim_values
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
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
RETURNS = {
    "Emission": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "inputs": "",
        "operation": "",
        "animals": ""
    }]
}
LOOKUPS = {
    "ecoalim-emissionsResourceUse": "emission-",
    "crop": "ecoalimMapping",
    "processedFood": "ecoalimMapping",
    "animalProduct": "ecoalimMapping",
    "forage": "ecoalimMapping",
    "feedFoodAdditive": "ecoalimMapping"
}
MODEL_KEY = 'cycle'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    if input.get('animal'):
        emission['animals'] = [input.get('animal')]
    return emission


def _add_emission(cycle: dict, input: dict):
    input_term_id = input.get('term', {}).get('@id')
    operation_term_id = input.get('operation', {}).get('@id')
    animal_term_id = input.get('animal', {}).get('@id')

    def add(prev: dict, mapping: tuple):
        gadm_id, ecoalim_key = mapping
        # all countries have the same coefficient
        coefficient = 1
        emissions = ecoalim_values(ecoalim_key, 'emission')
        for emission_term_id, value in emissions:
            # log run on each emission so we know it did run
            logShouldRun(cycle, MODEL, input_term_id, True, methodTier=TIER, emission_id=emission_term_id)
            debugValues(cycle, model=MODEL, term=emission_term_id, model_key=MODEL_KEY,
                        value=value,
                        coefficient=coefficient,
                        input=input_term_id,
                        operation=operation_term_id,
                        animal=animal_term_id)
            prev[emission_term_id] = prev.get(emission_term_id, []) + [value * coefficient]
        return prev
    return add


def _run_input(cycle: dict):
    no_gap_filled_background_emissions_func = no_gap_filled_background_emissions(cycle)

    def run(inputs: list):
        input = inputs[0]
        input_term_id = input.get('term', {}).get('@id')
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        mappings = get_input_mappings(MODEL, input)
        has_mappings = len(mappings) > 0

        # skip input that has background emissions we have already gap-filled (model run before)
        has_no_gap_filled_background_emissions = no_gap_filled_background_emissions_func(input)

        logRequirements(cycle, model=MODEL, term=input_term_id, model_key=MODEL_KEY,
                        has_ecoalim_mappings=has_mappings,
                        ecoalim_mappings=';'.join([v[1] for v in mappings]),
                        has_no_gap_filled_background_emissions=has_no_gap_filled_background_emissions,
                        input_value=input_value)

        should_run = all([has_mappings, has_no_gap_filled_background_emissions, input_value])
        logShouldRun(cycle, MODEL, input_term_id, should_run, methodTier=TIER, model_key=MODEL_KEY)

        grouped_emissions = reduce(_add_emission(cycle, input), mappings, {}) if should_run else {}
        return [
            _emission(term_id, mean(value) * input_value, input)
            for term_id, value in grouped_emissions.items()
        ]
    return run


def run(cycle: dict):
    inputs = get_background_inputs(cycle)
    grouped_inputs = reduce(group_by_keys(['term', 'operation', 'animal']), inputs, {})
    return flatten(map(_run_input(cycle), grouped_inputs.values()))
