from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from itertools import chain
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui_echarts.mixins import SpecMixin
from .types import TSpecData


@dataclass
class SpecCollector(SpecMixin):
    data: Optional[TSpecData] = None
    mark_specs: List[MarkSpecItem] = field(default_factory=list)
    echarts_option_spec: Optional[EChartsOptionSpecItem] = None

    def _create_data_map(self):
        data_id_count = 0
        id_map = {}
        data_map = {}

        for data in chain(
            [self.data] if self.data else [],
            (cs.data for cs in self.mark_specs if cs.data),
        ):
            data_id = str(data_id_count)
            id_map[id(data)] = data_id
            data_map[data_id] = _normalize_data(data)
            data_id_count += 1

        return data_map, id_map

    def to_option(self):
        data_map, id_map = self._create_data_map()

        config = {
            "dataMap": data_map,
            "dataId": id_map[id(self.data)] if self.data else None,
            "markSpecs": [cs.to_config(id_map) for cs in self.mark_specs],
            "echartsOptionSpec": self.echarts_option_spec.to_config()
            if self.echarts_option_spec
            else None,
        }

        ref_sets: List[RefSet] = []

        for data_key in data_map:
            data_item = data_map[data_key]
            if isinstance(data_item, ObservableMixin):
                ref_sets.append(RefSet(["dataMap", data_key], data_item))
                data_map[data_key] = None

        for idx, mark_spec in enumerate(config["markSpecs"]):
            ref_sets.extend(_extract_refs_from_dict(mark_spec, ["markSpecs", str(idx)]))

        if self.echarts_option_spec:
            ref_sets.extend(self.echarts_option_spec.gen_ref_set(["echartsOptionSpec"]))

        if ref_sets:
            return {
                **config,
                "refSets": [rs.to_config() for rs in ref_sets],
            }

        return config


@dataclass
class RefSet:
    path: List[str]
    ref: ObservableMixin

    def to_config(self):
        return {"path": self.path, "ref": self.ref._to_observable_config()}


@dataclass
class SpecItemMixin(ABC):
    def __add__(self, other: SpecItemMixin) -> SpecCollector:
        return self.with_in_collector(other.with_in_collector(SpecCollector()))

    def __radd__(self, other: SpecCollector) -> SpecCollector:
        return self.with_in_collector(other)

    @abstractmethod
    def with_in_collector(self, collector: SpecCollector) -> SpecCollector:
        pass

    def to_config(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class DatasetSpecItem(SpecItemMixin, SpecMixin):
    data: TSpecData

    def with_in_collector(self, collector: SpecCollector) -> SpecCollector:
        collector.data = self.data
        return collector

    def to_option(self):
        return SpecCollector(data=self.data).to_option()


@dataclass
class MarkSpecItem(SpecItemMixin, SpecMixin):
    type: str
    x: str
    y: str
    fx: Optional[str] = None
    fy: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    data: Optional[TSpecData] = None
    extends: Optional[Dict] = None

    def with_in_collector(self, collector: SpecCollector) -> SpecCollector:
        collector.mark_specs.append(self)
        return collector

    def to_config(self, id_map: Dict[int, str]):
        config = super().to_config()
        config["dataId"] = id_map[id(self.data)] if self.data else None
        del config["data"]

        if not self.extends:
            del config["extends"]
        return config

    def to_option(self):
        return SpecCollector(mark_specs=[self]).to_option()


@dataclass
class EChartsOptionSpecItem(SpecItemMixin, SpecMixin):
    dataset: List = field(default_factory=list)
    visual_map: Dict = field(default_factory=Dict)
    grid: Union[List[Dict], Dict, None] = None
    series: List = field(default_factory=list)
    xAxis: Union[List[Dict], Dict, None] = None
    yAxis: Union[List[Dict], Dict, None] = None
    tooltip: Dict = field(default_factory=Dict)
    title: Dict = field(default_factory=Dict)
    legend: Dict = field(default_factory=Dict)
    others: Dict = field(default_factory=Dict)

    def with_in_collector(self, collector: SpecCollector) -> SpecCollector:
        if not collector.echarts_option_spec:
            collector.echarts_option_spec = self
        else:
            collector.echarts_option_spec.dataset.extend(self.dataset)
            collector.echarts_option_spec.visual_map.update(self.visual_map)

            collector.echarts_option_spec._update_dict_or_list_config(
                collector.echarts_option_spec.grid, self.grid
            )
            collector.echarts_option_spec.series.extend(self.series)
            collector.echarts_option_spec._update_dict_or_list_config(
                collector.echarts_option_spec.xAxis, self.xAxis
            )
            collector.echarts_option_spec._update_dict_or_list_config(
                collector.echarts_option_spec.yAxis, self.yAxis
            )
            collector.echarts_option_spec.tooltip.update(self.tooltip)
            collector.echarts_option_spec.title.update(self.title)
            collector.echarts_option_spec.legend.update(self.legend)
            collector.echarts_option_spec.others.update(self.others)

        return collector

    def to_config(self):
        config = super().to_config()
        return {k: v for k, v in config.items() if v}

    def gen_ref_set(self, prefix_paths: List[str]):
        yield from _extract_refs_from_dict(super().to_config(), prefix_paths)

    @staticmethod
    def _update_dict_or_list_config(
        config: Union[Dict, List[Dict], None], updates: Union[Dict, List[Dict], None]
    ):
        if not config or not updates:
            return

        if isinstance(config, list) and isinstance(updates, list):
            config.extend(updates)
            return

        if isinstance(config, dict) and isinstance(updates, dict):
            config.update(updates)
            return

        raise ValueError("config and updates should be both dict or list")

    def to_option(self):
        return SpecCollector(echarts_option_spec=self).to_option()


def _extract_refs_from_dict(
    config: Dict[str, Any], prefix_paths: Optional[List[str]] = None
):
    prefix_paths = prefix_paths or []

    stack = list((prefix_paths + [k], v, config, k) for k, v in config.items())
    while stack:
        paths, item, org_dict, current_key = stack.pop()
        if isinstance(item, ObservableMixin):
            yield RefSet(paths, item)
            org_dict[current_key] = None
            continue
        if isinstance(item, dict):
            stack.extend((paths + [k], v, item, k) for k, v in item.items())


def _normalize_data(data: TSpecData):
    if isinstance(data, list):
        columns = list(data[0].keys())
        rows = [list(r.values()) for r in data]
        return {"fields": columns, "rows": rows}

    if isinstance(data, dict):
        return data

    if isinstance(data, ObservableMixin):
        return data

    raise ValueError("Unsupported data type")
