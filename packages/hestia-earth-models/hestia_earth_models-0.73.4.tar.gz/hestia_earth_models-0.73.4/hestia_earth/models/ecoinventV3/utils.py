from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.utils.term import get_lookup_value


def get_input_mappings(model: str, cycle: dict, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoinventMapping', model=model, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    return [(m.split(':')[0], float(m.split(':')[1])) for m in mappings]
