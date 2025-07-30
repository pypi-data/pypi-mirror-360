from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission, get_nh3_no3_nox_to_n
from hestia_earth.models.utils.cycle import get_ecoClimateZone
from .utils import ecoClimate_factors, EF4_FACTORS, EF5_FACTORS
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "no3ToGroundwaterOrganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "nh3ToAirOrganicFertiliser"},
            {"@type": "Emission", "value": "", "term.@id": "noxToAirOrganicFertiliser"}
        ],
        "optional": {
            "site": {
                "@type": "Site",
                "measurements": [
                    {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
                ]
            }
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2OToAirOrganicFertiliserIndirect'
TIER = EmissionMethodTier.TIER_1.value
NO3_TERM_ID = 'no3ToGroundwaterOrganicFertiliser'
NH3_TERM_ID = 'nh3ToAirOrganicFertiliser'
NOX_TERM_ID = 'noxToAirOrganicFertiliser'


def _emission(value: float, min: float, max: float, aggregated: bool = False):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['min'] = [min]
    emission['max'] = [max]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['methodModelDescription'] = 'Aggregated version' if aggregated else 'Disaggregated version'
    return emission


def _run(cycle: dict, no3: float, nh3: float, nox: float):
    ecoClimateZone = get_ecoClimateZone(cycle)

    ef4, aggregated = ecoClimate_factors(EF4_FACTORS, ecoClimateZone=ecoClimateZone)
    ef5 = EF5_FACTORS.get('default')

    debugValues(cycle, model=MODEL, term=TERM_ID,
                ecoClimateZone=ecoClimateZone,
                ef4_factors_used=log_as_table(ef4),
                ef5_factors_used=log_as_table(ef5),
                aggregated=aggregated)

    value = sum([
        no3 * ef5['value'],
        nh3 * ef4['value'],
        nox * ef4['value']
    ]) * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    min = sum([
        no3 * ef5['min'],
        nh3 * ef4['min'],
        nox * ef4['min']
    ]) * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    max = sum([
        no3 * ef5['max'],
        nh3 * ef4['max'],
        nox * ef4['max']
    ]) * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value, min, max, aggregated=aggregated)]


def _should_run(cycle: dict):
    nh3_n, no3_n, nox_n = get_nh3_no3_nox_to_n(cycle, NH3_TERM_ID, NO3_TERM_ID, NOX_TERM_ID)
    term_type_complete = _is_term_type_complete(cycle, 'fertiliser')

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    no3_n=no3_n,
                    nh3_n=nh3_n,
                    nox_n=nox_n,
                    term_type_fertiliser_complete=term_type_complete)

    should_run = all([no3_n is not None, nh3_n is not None, nox_n is not None, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, no3_n, nh3_n, nox_n


def run(cycle: dict):
    should_run, no3, nh3, nox = _should_run(cycle)
    return _run(cycle, no3, nh3, nox) if should_run else []
