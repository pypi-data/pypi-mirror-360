from typing import Dict, List, Union, TypedDict
from instaui.vars.mixin_types.observable import ObservableMixin


class TSpecDataDict(TypedDict):
    fields: List[str]
    rows: List[List]


TSpecData = Union[List[Dict], TSpecDataDict, ObservableMixin]
