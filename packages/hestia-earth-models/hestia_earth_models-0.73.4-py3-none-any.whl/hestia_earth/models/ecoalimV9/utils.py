from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, lookup_columns
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.utils.term import get_lookup_value


_LOOKUP = "ecoalim-emissionsResourceUse.csv"


def get_input_mappings(model: str, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoalimMapping', model=model, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    return [(m.split(':')[0], m.split(':')[1]) for m in mappings]


def ecoalim_values(mapping: str, column_prefix: str):
    lookup = download_lookup(_LOOKUP)
    col_name = column_name('ecoalimMappingName')

    def emission(column: str):
        id = get_table_value(lookup, col_name, mapping, column)
        value = get_table_value(lookup, col_name, mapping, column.replace('term', 'value'))
        return (id, value) if id else None

    columns = [
        col for col in lookup_columns(lookup)
        if col.startswith(column_name(column_prefix)) and col.endswith(column_name('term'))
    ]
    return non_empty_list(map(emission, columns))
