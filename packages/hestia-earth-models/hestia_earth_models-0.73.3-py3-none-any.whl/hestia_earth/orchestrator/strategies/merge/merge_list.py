import pydash
from datetime import datetime
from hestia_earth.schema import UNIQUENESS_FIELDS
from hestia_earth.utils.tools import safe_parse_date

from hestia_earth.orchestrator.utils import _non_empty_list, update_node_version
from .merge_node import merge as merge_node

_METHOD_MODEL_KEY = 'methodModel.@id'


def _matching_properties(model: dict, node_type: str):
    return UNIQUENESS_FIELDS.get(node_type, {}).get(model.get('key'), [])


def _has_property(value: dict, key: str):
    keys = key.split('.')
    is_list = len(keys) >= 2 and isinstance(pydash.objects.get(value, keys[0]), list)
    values = [
        pydash.objects.get(v, '.'.join(keys[1:])) for v in pydash.objects.get(value, keys[0])
    ] if is_list else [
        pydash.objects.get(value, key)
    ]
    return all([v is not None for v in values])


def _values_have_property(values: list, key: str): return any([_has_property(v, key) for v in values])


def _match_list_el(source: list, dest: list, key: str):
    src_value = sorted(_non_empty_list([pydash.objects.get(x, key) for x in source]))
    dest_value = sorted(_non_empty_list([pydash.objects.get(x, key) for x in dest]))
    return src_value == dest_value


def _get_value(data: dict, key: str, merge_args: dict = {}):
    value = pydash.objects.get(data, key)
    date = safe_parse_date(value) if key in ['startDate', 'endDate'] else None
    return datetime.strftime(date, merge_args.get('matchDatesFormat', '%Y-%m-%d')) if date else value


def _match_el(source: dict, dest: dict, keys: list, merge_args: dict = {}):
    def match(key: str):
        keys = key.split('.')
        src_value = _get_value(source, key, merge_args)
        dest_value = _get_value(dest, key, merge_args)
        is_list = len(keys) >= 2 and (
            isinstance(pydash.objects.get(source, keys[0]), list) or
            isinstance(pydash.objects.get(dest, keys[0]), list)
        )
        return _match_list_el(
            pydash.objects.get(source, keys[0], []),
            pydash.objects.get(dest, keys[0], []),
            '.'.join(keys[1:])
        ) if is_list else src_value == dest_value

    source_properties = [p for p in keys if _has_property(source, p)]
    dest_properties = [p for p in keys if _has_property(dest, p)]

    return all(map(match, source_properties)) if source_properties == dest_properties else False


def _handle_local_property(values: list, properties: list, local_id: str):
    # Handle "impactAssessment.@id" if present in the data
    existing_id = local_id.replace('.id', '.@id')

    if local_id in properties:
        # remove if not used
        if not _values_have_property(values, local_id):
            properties.remove(local_id)

        # add if used
        if _values_have_property(values, existing_id):
            properties.append(existing_id)

    return properties


def _find_match_el_index(values: list, el: dict, same_methodModel: bool, model: dict, node_type: str, merge_args: dict):
    """
    Find an element in the values that match the new element, based on the unique properties.
    To find a matching element:

    1. Update list of properties to handle `methodModel.@id` and `impactAssessment.@id`
    2. Filter values that have the same unique properties as el
    3. Make sure all shared unique properties are identical
    """
    properties = _matching_properties(model, node_type)
    properties = list(set(properties + [_METHOD_MODEL_KEY])) if same_methodModel else [
        p for p in properties if p != _METHOD_MODEL_KEY
    ]
    properties = _handle_local_property(values, properties, 'impactAssessment.id')

    return next(
        (i for i in range(len(values)) if _match_el(values[i], el, properties, merge_args)),
        None
    ) if properties else None


def merge(source: list, merge_with: list, version: str, model: dict = {}, merge_args: dict = {}, node_type: str = ''):
    source = source if source is not None else []

    # only merge node if it has the same `methodModel`
    same_methodModel = merge_args.get('sameMethodModel', False)
    # only merge if the
    skip_same_term = merge_args.get('skipSameTerm', False)

    for el in _non_empty_list(merge_with):
        source_index = _find_match_el_index(source, el, same_methodModel, model, node_type, merge_args)
        if source_index is None:
            source.append(update_node_version(version, el))
        elif not skip_same_term:
            source[source_index] = merge_node(source[source_index], el, version, model, merge_args)
    return source
