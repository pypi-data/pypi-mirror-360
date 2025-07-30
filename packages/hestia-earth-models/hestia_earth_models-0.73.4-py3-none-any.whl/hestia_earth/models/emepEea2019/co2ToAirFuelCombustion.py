from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.completeness import _is_term_type_complete
from .utils import get_fuel_inputs, group_fuel_inputs, _emission, _run_inputs
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "or": {
            "inputs": [
                {"@type": "Input", "value": "", "term.termType": "fuel", "optional": {
                    "operation": ""
                }}
            ],
            "completeness.electricityFuel": "True"
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "inputs": "",
        "operation": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "fuel": "co2ToAirFuelCombustionEmepEea2019",
    "operation": "co2ToAirFuelCombustionEmepEea2019"
}
TERM_ID = 'co2ToAirFuelCombustion'
TIER = EmissionMethodTier.TIER_1.value


def _should_run(cycle: dict):
    electricity_complete = _is_term_type_complete(cycle, 'electricityFuel')
    fuel_inputs, valid_inputs = get_fuel_inputs(TERM_ID, cycle, LOOKUPS['fuel'])

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    termType_electricityFuel_complete=electricity_complete,
                    fuel_inputs=log_as_table(fuel_inputs))

    should_run = any([bool(valid_inputs), electricity_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, group_fuel_inputs(valid_inputs)


def run(cycle: dict):
    should_run, fuel_inputs = _should_run(cycle)
    return (
        [
            _run_inputs(inputs, tier=TIER, term_id=TERM_ID)
            for inputs in fuel_inputs.values()
        ] if fuel_inputs else [
            _emission(value=0, tier=TIER, term_id=TERM_ID)
        ]
    ) if should_run else []
