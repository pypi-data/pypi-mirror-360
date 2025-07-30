from pathlib import Path
from typing import Dict, Optional, Set, Union
from instaui import ui
from instaui.event.event_mixin import EventMixin
from .types import TInitOptions, TResizeOptions, TEChartsEvent, TZRenderEvent
from .mixins import SpecMixin

_STATIC_DIR = Path(__file__).parent / "static"
_ECHARTS_JS_FILE = _STATIC_DIR / "echarts.esm.min.js"


_IMPORT_MAPS = {
    "echarts": _ECHARTS_JS_FILE,
}


class ECharts(
    ui.element,
    esm="./static/instaui-echarts.js",
    externals=_IMPORT_MAPS,
):
    """Create an ECharts component

    Args:
        option (ui.TMaybeRef[Dict]): Chart option.
        theme (Optional[Union[Path, str, Dict]], optional): Theme file or object. Defaults to None.
        init_options (Optional[TInitOptions], optional): Chart initialization options. Defaults to None.
        update_options (Optional[Dict], optional): Chart update options. Defaults to None.
        resize_options (Optional[TResizeOptions], optional): Chart resize options. Defaults to None.

    Example usage:

    resize_options:

    .. code-block:: python
        ui.echarts(opts, resize_options={"throttle": 100})

    chart event:
    .. code-block:: python
        opts = ui.state(
            {
                "title": {"text": "ECharts Getting Started Example"},
                "tooltip": {},
                "legend": {"data": ["sales"]},
                "xAxis": {
                    "data": ["Shirts", "Cardigans", "Chiffons", "Pants", "Heels", "Socks"]
                },
                "yAxis": {},
                "series": [
                    {"name": "sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}
                ],
            }
        )

        msg = ui.state("Click the bars in the chart.")

        @ui.event(inputs=[ui.event_context.e()], outputs=[msg])
        def click(arg):
            return f'You clicked on "{arg["name"]}"'

        ui.content(msg)
        ui.echarts(opts).on_chart("click", click)

    """

    def __init__(
        self,
        option: Union[ui.TMaybeRef[Dict], SpecMixin],
        *,
        theme: Optional[Union[Path, str, Dict]] = None,
        init_options: Optional[TInitOptions] = None,
        update_options: Optional[Dict] = None,
        resize_options: Optional[TResizeOptions] = None,
    ):
        super().__init__()
        self._set_var_getter_strategy("all")

        option_type = "graph" if isinstance(option, SpecMixin) else "dict"
        if isinstance(option, SpecMixin):
            option = option.to_option()  # type: ignore

        self._chart_events: Set[str] = set()
        self._zr_events: Set[str] = set()
        self.props({"option": option, "optionType": option_type})

        if init_options is not None:
            self.props({"initOptions": init_options})

        if update_options:
            self.props({"updateOptions": update_options})

        if theme:
            if isinstance(theme, (str, Path)):
                raise NotImplementedError("Theme file not supported yet")
            else:
                self.props({"theme": theme})

        self.props({"resizeOption": resize_options or {}})

        self.style("width: 100%; height: 100%;min-width:0;")

    def on_chart(
        self,
        event_name: TEChartsEvent,
        handler: EventMixin,
    ):
        self._chart_events.add(event_name)
        return self.on(f"chart:{event_name}", handler)

    def on_zr(self, event_name: TZRenderEvent, handler: EventMixin):
        self._zr_events.add(event_name)
        return self.on(f"zr:{event_name}", handler)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        props = data.get("props", {})

        if self._chart_events:
            props["chartEvents"] = list(self._chart_events)

        if self._zr_events:
            props["zrEvents"] = list(self._zr_events)

        return data
