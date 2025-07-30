from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.model import linked_node

from .method import include_methodModel
from .term import download_term


def _new_indicator(term, model=None, land_cover_id: str = None, previous_land_cover_id: str = None):
    node = {'@type': SchemaType.INDICATOR.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_term(
        term, TermTermType.CHARACTERISEDINDICATOR)
    )
    if land_cover_id:
        node['landCover'] = linked_node(download_term(land_cover_id, TermTermType.LANDCOVER))
    if previous_land_cover_id:
        node['previousLandCover'] = linked_node(download_term(previous_land_cover_id, TermTermType.LANDCOVER))
    return include_methodModel(node, model)
