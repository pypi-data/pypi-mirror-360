from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten
from hestia_earth.utils.emission import cycle_emissions_in_system_boundary

from hestia_earth.models.log import logShouldRun
from . import is_from_model
from .term import get_lookup_value


def _animal_inputs(animal: dict):
    inputs = animal.get('inputs', [])
    return [(input | {'animal': animal.get('term', {})}) for input in inputs]


def _should_run_input(products: list):
    def should_run(input: dict):
        return all([
            # make sure Input is not a Product as well or we might double-count emissions
            find_term_match(products, input.get('term', {}).get('@id'), None) is None,
            # ignore inputs which are flagged as Product of the Cycle
            not input.get('fromCycle', False),
            not input.get('producedInCycle', False)
        ])
    return should_run


def get_background_inputs(cycle: dict, extra_inputs: list = []):
    # add all the properties of some Term that inlcude others with the mapping
    inputs = flatten(
        cycle.get('inputs', []) +
        list(map(_animal_inputs, cycle.get('animals', []))) +
        extra_inputs
    )
    return list(filter(_should_run_input(cycle.get('products', [])), inputs))


def no_gap_filled_background_emissions(
    node: dict, list_key: str = 'emissions', term_type: TermTermType = TermTermType.EMISSION
):
    blank_nodes = filter_list_term_type(node.get(list_key, []), term_type)

    def check_input(input: dict):
        input_term_id = input.get('term', {}).get('@id')
        operation_term_id = input.get('operation', {}).get('@id')
        animal_term_id = input.get('animal', {}).get('@id')

        return not any([
            is_from_model(blank_node)
            for blank_node in blank_nodes
            if all([
                any([i.get('@id') == input_term_id for i in blank_node.get('inputs', [])]),
                blank_node.get('operation', {}).get('@id') == operation_term_id,
                blank_node.get('animal', {}).get('@id') == animal_term_id
            ])
        ])

    return check_input


def all_background_emission_term_ids(cycle: dict):
    term_ids = cycle_emissions_in_system_boundary(cycle)
    return list(set([
        get_lookup_value({'termType': TermTermType.EMISSION.value, '@id': term_id}, 'inputProductionGroupId')
        for term_id in term_ids
    ]))


def log_missing_emissions(cycle: dict, **log_args):
    all_emission_term_ids = all_background_emission_term_ids(cycle)

    def log_input(input_term_id: str, included_emission_term_ids: list, **extra_log_args):
        missing_emission_term_ids = [
            term_id for term_id in all_emission_term_ids if term_id not in included_emission_term_ids
        ]
        for emission_id in missing_emission_term_ids:
            logShouldRun(cycle, term=input_term_id, should_run=False, emission_id=emission_id,
                         **log_args,
                         **extra_log_args)
    return log_input
