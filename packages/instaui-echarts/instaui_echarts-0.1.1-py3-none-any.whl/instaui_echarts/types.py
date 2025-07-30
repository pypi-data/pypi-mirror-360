from typing import Literal, Union
from typing_extensions import TypedDict


TEChartsEvent = Literal[
    "highlight",
    "downplay",
    "selectchanged",
    "legendselectchanged",
    "legendselected",
    "legendunselected",
    "legendselectall",
    "legendinverseselect",
    "legendscroll",
    "datazoom",
    "datarangeselected",
    "timelinechanged",
    "timelineplaychanged",
    "restore",
    "dataviewchanged",
    "magictypechanged",
    "geoselectchanged",
    "geoselected",
    "geounselected",
    "axisareaselected",
    "brush",
    "brushEnd",
    "brushselected",
    "globalcursortaken",
    "rendered",
    "finished",
    "click",
    "dblclick",
    "mouseover",
    "mouseout",
    "mousemove",
    "mousedown",
    "mouseup",
    "globalout",
    "contextmenu",
]


TZRenderEvent = Literal[
    "click", "mousedown", "mouseup", "mousewheel", "dblclick", "contextmenu"
]


class TResizeOptions(TypedDict, total=False):
    throttle: int


class TInitOptions(TypedDict, total=False):
    devicePixelRatio: int
    renderer: Literal["canvas", "svg"]
    width: Union[int, str]
    height: Union[int, str]
    locale: str
    pointerSize: int
