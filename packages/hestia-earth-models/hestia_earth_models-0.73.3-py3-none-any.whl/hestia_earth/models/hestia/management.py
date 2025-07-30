from typing import List
from datetime import timedelta, datetime
from hestia_earth.schema import SchemaType, TermTermType, SiteSiteType, COMPLETENESS_MAPPING
from hestia_earth.utils.lookup import column_name, get_table_value, download_lookup
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float, flatten
from hestia_earth.utils.blank_node import get_node_value

from hestia_earth.models.log import logRequirements, logShouldRun, log_as_table
from hestia_earth.models.utils import _include, group_by
from hestia_earth.models.utils.management import _new_management
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.blank_node import condense_nodes, DatestrFormat, _gapfill_datestr, DatestrGapfillMode
from hestia_earth.models.utils.crop import get_landCover_term_id
from hestia_earth.models.utils.site import (
    related_cycles, get_land_cover_term_id as get_landCover_term_id_from_site_type
)
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "related": {
            "Cycle": [{
                "@type": "Cycle",
                "endDate": "",
                "practices": [
                    {
                        "@type": "Practice",
                        "term.termType": [
                            "waterRegime",
                            "tillage",
                            "cropResidueManagement",
                            "landUseManagement",
                            "pastureManagement",
                            "system",
                            "landCover"
                        ],
                        "value": ""
                    }
                ],
                "inputs": [
                    {
                        "@type": "Input",
                        "term.termType": [
                            "inorganicFertiliser",
                            "organicFertiliser",
                            "soilAmendment"
                        ]
                    }
                ],
                "optional": {
                    "startDate": "",
                    "cycleDuration": ""
                }
            }]
        }
    }
}
RETURNS = {
    "Management": [{
        "term.termType": [
            "landCover", "waterRegime", "tillage", "cropResidueManagement", "landUseManagement", "system"
        ],
        "value": "",
        "endDate": "",
        "startDate": ""
    }]
}
LOOKUPS = {
    "crop": ["landCoverTermId", "maximumCycleDuration"],
    "forage": ["landCoverTermId"],
    "inorganicFertiliser": "nitrogenContent",
    "organicFertiliser": "ANIMAL_MANURE",
    "soilAmendment": "PRACTICE_INCREASING_C_INPUT",
    "landUseManagement": "GAP_FILL_TO_MANAGEMENT",
    "property": "GAP_FILL_TO_MANAGEMENT"
}
MODEL_KEY = 'management'

_PRACTICES_TERM_TYPES = [
    TermTermType.WATERREGIME,
    TermTermType.TILLAGE,
    TermTermType.CROPRESIDUEMANAGEMENT,
    TermTermType.LANDUSEMANAGEMENT,
    TermTermType.PASTUREMANAGEMENT,
    TermTermType.SYSTEM,
    TermTermType.LANDCOVER
]
_PRACTICES_COMPLETENESS_MAPPING = COMPLETENESS_MAPPING.get(SchemaType.PRACTICE.value, {})
_ANIMAL_MANURE_USED_TERM_ID = "animalManureUsed"
_INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID = "inorganicNitrogenFertiliserUsed"
_ORGANIC_FERTILISER_USED_TERM_ID = "organicFertiliserUsed"
_AMENDMENT_INCREASING_C_USED_TERM_ID = "amendmentIncreasingSoilCarbonUsed"
_INPUT_RULES = {
    TermTermType.INORGANICFERTILISER.value: (
        (
            TermTermType.INORGANICFERTILISER.value,  # Lookup column
            lambda x: safe_parse_float(x, default=0) > 0,  # Condition
            _INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID  # New term.
        ),
    ),
    TermTermType.SOILAMENDMENT.value: (
        (
            TermTermType.SOILAMENDMENT.value,
            lambda x: bool(x) is True,
            _AMENDMENT_INCREASING_C_USED_TERM_ID
        ),
    ),
    TermTermType.ORGANICFERTILISER.value: (
        (
            TermTermType.SOILAMENDMENT.value,
            lambda x: bool(x) is True,
            _ORGANIC_FERTILISER_USED_TERM_ID
        ),
        (
            TermTermType.ORGANICFERTILISER.value,
            lambda x: bool(x) is True,
            _ANIMAL_MANURE_USED_TERM_ID
        )
    )
}
_SKIP_LAND_COVER_SITE_TYPES = [
    SiteSiteType.CROPLAND.value
]


def management(data: dict):
    node = _new_management(data.get('id'))
    node['value'] = data['value']
    node['endDate'] = _gap_filled_date_only_str(data['endDate'])
    if data.get('startDate'):
        node['startDate'] = _gap_filled_date_only_str(date_str=data['startDate'], mode=DatestrGapfillMode.START)
    if data.get('properties'):
        node['properties'] = data['properties']
    return node


def _get_cycle_duration(cycle: dict, land_cover_id: str = None):
    cycle_duration = cycle.get('cycleDuration')
    lookup_value = None if cycle_duration or not land_cover_id else safe_parse_float(get_table_value(
        download_lookup("crop.csv"),
        column_name('landCoverTermId'),
        land_cover_id,
        column_name('maximumCycleDuration')
    ), default=None)
    return cycle_duration or lookup_value


def _gap_filled_date_only_str(date_str: str, mode: str = DatestrGapfillMode.END) -> str:
    return _gapfill_datestr(datestr=date_str, mode=mode)[:10]


def _gap_filled_date_obj(date_str: str, mode: str = DatestrGapfillMode.END) -> datetime:
    return datetime.strptime(
        _gap_filled_date_only_str(date_str=date_str, mode=mode),
        DatestrFormat.YEAR_MONTH_DAY.value
    )


def _gap_filled_start_date(cycle: dict, end_date: str, land_cover_id: str = None) -> dict:
    """If possible, gap-fill the startDate based on the endDate - cycleDuration"""
    cycle_duration = _get_cycle_duration(cycle, land_cover_id)
    return {
        "startDate": (
            _gap_filled_date_obj(cycle.get("startDate"), mode=DatestrGapfillMode.START) if cycle.get("startDate") else
            _gap_filled_date_obj(end_date) - timedelta(days=cycle_duration - 1)
        )
    } if any([cycle_duration, cycle.get("startDate")]) else {}


def _include_with_date_gap_fill(value: dict, keys: list) -> dict:
    return {
        k: (
            _gap_filled_date_only_str(v) if k == "endDate" else
            _gap_filled_date_only_str(v, mode=DatestrGapfillMode.START) if k == "startDate" else
            v
        )
        for k, v in value.items() if k in keys
    }


def _should_gap_fill(term: dict):
    value = get_lookup_value(lookup_term=term, column='GAP_FILL_TO_MANAGEMENT')
    return bool(value)


def _map_to_value(value: dict):
    return {
        'id': value.get('term', {}).get('@id'),
        'value': value.get('value'),
        'startDate': value.get('startDate'),
        'endDate': value.get('endDate'),
        'properties': value.get('properties')
    }


def _extract_node_value(node: dict) -> dict:
    return node | {'value': get_node_value(node)}


def _get_relevant_items(cycle: dict, item_name: str, term_types: List[TermTermType], completeness_mapping: dict = {}):
    """
    Get items from the list of cycles with any of the relevant terms.
    Also adds dates from Cycle.
    """
    # filter term types that are no complete
    complete_term_types = term_types if not completeness_mapping else [
        term_type for term_type in term_types
        if any([
            not completeness_mapping.get(term_type.value),
            cycle.get('completeness', {}).get(completeness_mapping.get(term_type.value), False)
        ])
    ]
    blank_nodes = filter_list_term_type(cycle.get(item_name, []), complete_term_types)
    return [
        _include_with_date_gap_fill(cycle, ["startDate", "endDate"]) |
        _include(
            _gap_filled_start_date(
                cycle=cycle,
                end_date=item.get("endDate") if "endDate" in item else cycle.get("endDate", ""),
                land_cover_id=get_landCover_term_id(item.get('term', {})),
            ) if "startDate" not in item else {},
            "startDate"
        ) |
        item
        for item in blank_nodes
    ]


def _process_rule(node: dict, term: dict) -> list:
    term_types = []
    for column, condition, new_term in _INPUT_RULES[term.get('termType')]:
        lookup_result = get_lookup_value(term, LOOKUPS[column], model=MODEL, term=term.get('@id'), model_key=MODEL_KEY)

        if condition(lookup_result):
            term_types.append(node | {'id': new_term})

    return term_types


def _run_from_inputs(site: dict, cycle: dict) -> list:
    inputs = flatten([
        _process_rule(node={
            'value': True,
            'startDate': cycle.get('startDate'),
            'endDate': cycle.get('endDate')
        }, term=input.get('term'))
        for input in cycle.get('inputs', [])
        if input.get('term', {}).get('termType') in _INPUT_RULES
    ])
    return inputs


def _run_from_siteType(site: dict, cycle: dict):
    site_type = site.get('siteType')
    site_type_id = get_landCover_term_id_from_site_type(site_type) if site_type not in _SKIP_LAND_COVER_SITE_TYPES \
        else None
    start_date = cycle.get('startDate') or _gap_filled_start_date(
        cycle=cycle,
        end_date=cycle.get('endDate'),
        land_cover_id=site_type_id
    ).get('startDate')

    should_run = all([site_type_id, start_date])
    return [{
        'id': site_type_id,
        'value': 100,
        'startDate': start_date,
        'endDate': cycle.get('endDate')
    }] if should_run else []


def _should_run_practice(practice: dict):
    """
    Include only landUseManagement practices where GAP_FILL_TO_MANAGEMENT = True
    """
    term = practice.get('term', {})
    return term.get('termType') != TermTermType.LANDUSEMANAGEMENT.value or _should_gap_fill(term)


def _run_from_practices(cycle: dict):
    practices = [
        _extract_node_value(
            _include_with_date_gap_fill(
                value=practice,
                keys=["term", "value", "startDate", "endDate", "properties"]
            )
        ) for practice in _get_relevant_items(
            cycle=cycle,
            item_name="practices",
            term_types=_PRACTICES_TERM_TYPES,
            completeness_mapping=_PRACTICES_COMPLETENESS_MAPPING
        )
    ]
    return list(map(_map_to_value, filter(_should_run_practice, practices)))


def _run_cycle(site: dict, cycle: dict):
    inputs = _run_from_inputs(site, cycle)
    site_types = _run_from_siteType(site=site, cycle=cycle)
    practices = _run_from_practices(cycle)
    return [
        node | {'cycle-id': cycle.get('@id')}
        for node in inputs + site_types + practices
    ]


def run(site: dict):
    cycles = related_cycles(site)
    nodes = flatten([_run_cycle(site=site, cycle=cycle) for cycle in cycles])

    # group nodes with same `id` to display as a single log per node
    grouped_nodes = group_by(nodes, ['id'])
    for id, values in grouped_nodes.items():
        logRequirements(
            site,
            model=MODEL,
            term=id,
            model_key=MODEL_KEY,
            details=log_as_table(values, ignore_keys=['id', 'properties']),
        )
        logShouldRun(site, MODEL, id, True, model_key=MODEL_KEY)

    return condense_nodes(list(map(management, nodes)))
