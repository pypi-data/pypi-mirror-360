from typing import Dict, List, Optional, Union
from ._spec import DatasetSpecItem, MarkSpecItem, EChartsOptionSpecItem
from .types import TSpecData


class data(DatasetSpecItem):
    def __init__(self, source: TSpecData):
        super().__init__(source)


def title(text: str, other: Optional[Dict] = None):
    return option(title={"text": text, **(other or {})})


def line(
    *,
    x: str,
    y: str,
    fx: Optional[str] = None,
    fy: Optional[str] = None,
    color: Optional[str] = None,
    data: Optional[TSpecData] = None,
):
    return MarkSpecItem(type="line", x=x, y=y, fx=fx, fy=fy, color=color, data=data)


def bar_y(
    *,
    x: str,
    y: str,
    fx: Optional[str] = None,
    fy: Optional[str] = None,
    color: Optional[str] = None,
    stack: Optional[str] = None,
    extends: Optional[Dict] = None,
    data: Optional[TSpecData] = None,
):
    extends = extends or {}
    if stack:
        extends["stack"] = stack

    return MarkSpecItem(
        type="barY", x=x, y=y, fx=fx, fy=fy, color=color, extends=extends, data=data
    )


def point(
    *,
    x: str,
    y: str,
    fx: Optional[str] = None,
    fy: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    data: Optional[TSpecData] = None,
):
    return MarkSpecItem(
        type="point", x=x, y=y, fx=fx, fy=fy, size=size, color=color, data=data
    )


def option(
    *,
    dataset: Optional[List[Dict]] = None,
    visual_map: Optional[Dict] = None,
    grid: Optional[Union[List[Dict], Dict]] = None,
    series: Optional[List[Dict]] = None,
    xaxis: Optional[Union[List[Dict], Dict]] = None,
    yaxis: Optional[Union[List[Dict], Dict]] = None,
    tooltip: Optional[Dict] = None,
    legend: Optional[Dict] = None,
    title: Optional[Dict] = None,
    other: Optional[Dict] = None,
):
    return EChartsOptionSpecItem(
        dataset=dataset or [],
        visual_map=visual_map or {},
        grid=grid,
        series=series or [],
        xAxis=xaxis,
        yAxis=yaxis,
        tooltip=tooltip or {},
        legend=legend or {},
        title=title or {},
        others=other or {},
    )
