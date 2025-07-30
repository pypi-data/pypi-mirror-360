"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2025-06-21 20:31:04
Copyright © Kaluluosi All rights reserved
"""

import math
from nicegui import app, ui
from nicegui.events import GenericEventArguments
from contextlib import contextmanager

from pydantic import BaseModel, Field, RootModel


class SerieData(BaseModel):
    name: str
    type: str = "line"
    data: list[float] = Field(default_factory=list)
    showSymbol: bool = False
    lineStyle: dict = Field(default_factory=lambda: {"normal": {"width": 1}})


Series = RootModel[list[SerieData]]


class MonitorTabPanel(ui.tab_panel):
    def __init__(self, name: str | ui.tab) -> None:
        super().__init__(name)
        self.classes("w-full")


class ControlCard(ui.card):
    def __init__(self) -> None:
        super().__init__()
        self.tight()
        self.classes("w-full")

    @contextmanager
    def session(self):
        with ui.card_section().classes("w-full"):
            with ui.row().classes("items-center w-full"):
                yield

    @contextmanager
    def actions(self):
        with ui.card_actions().classes("w-full"):
            yield


class Drawer(ui.drawer):
    def __init__(self) -> None:
        super().__init__(side="right", value=True, elevated=True)
        self.bind_value(app.storage.general, "android_profiler_drawer_expand")
        self.classes("p-0")
        self.props("width=400")

        with ui.page_sticky(position="top-right", y_offset=100).style("z-index:2000"):
            self.btn_expand = ui.button(
                icon="arrow_left", on_click=lambda: self.toggle()
            )
            self.btn_expand.classes("pl-2 pr-2 pt-8 pb-8 w-1")
            self.btn_expand.style("border-radius:3px 0px 0px 3px;")

    @contextmanager
    def create_tabs(self):
        self.tabs = ui.tabs()
        with self.tabs:
            yield

    @contextmanager
    def create_tab_panels(self):
        self.tab_panels = ui.tab_panels(self.tabs).classes("w-full")
        with self.tab_panels:
            yield


class MonitorCard(ui.card):
    title: str = "Monitor"
    description: str = ""

    def __init__(
        self,
        y_axis_unit: str = "",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__()
        self.classes("w-full")
        self._group = group
        self._series: list[SerieData] = []
        self._y_unit = y_axis_unit
        self.show_aggregate = show_aggregate

        with self:
            with self.session():
                with ui.row().classes("justify-between items-center w-full"):
                    self.label_title = ui.label(self.title).classes("text-xl")
                    self.label_descrip = ui.label(self.description)
                ui.separator()

            self.chart = ui.echart(
                {
                    "legend": {"orient": "vertical", "left": 10, "selected": {}},
                    "grid": {
                        "left": "140px",
                        "right": "4%",
                        "top": "3%",
                        "bottom": "10%",
                        "containLabel": True,
                    },
                    "xAxis": {
                        "type": "category",
                        "axisLabel": {"formatter": "{value}s"},
                    },
                    "yAxis": {
                        "type": "value",
                        "axisLabel": {"formatter": f"{{value}}{self._y_unit}"},
                    },
                    "series": [],
                    "axisPointer": {
                        "link": {"xAxisIndex": "all"},
                        "label": {"backgroundColor": "#777"},
                    },
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "cross"},
                        "backgroundColor": "rgba(255, 255, 255, 0.8)",
                        "position": "js:function (pos, params, el, elRect, size) { var obj = { top: 10 }; obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30; return obj; }",
                        "extraCssText": "width: 170px",
                    },
                    "dataZoom": [
                        {
                            "type": "slider",
                            "show": True,
                            "zoomOnMouseWheel": False,
                            "moveOnMouseWheel": False,
                            "start": 0,
                            "end": 100,
                        },
                    ],
                }
            )

        self.chart.on("chart:datazoom", self._handle_datazoom)
        self.chart.on("chart:legendselectchanged", self._handle_legendselectchanged)

        if self.show_aggregate:
            self._create_aggregate()

        ui.run_javascript(
            f"""
            let chart = echarts.getInstanceByDom(document.getElementById('{self.chart.html_id}'));
            chart.group = '{self.group}';
            """
        )

    @property
    def group(self) -> str:
        return self._group

    @property
    def dataZoom(self):
        storage_datazoom = app.storage.general.get("android_profiler_datazoom", {})
        datazoom = {
            "start": storage_datazoom.get("start", 0),
            "end": storage_datazoom.get("end", 100),
        }
        return datazoom

    @property
    def legend_selected(self):
        return app.storage.general.get("android_profiler_legend", {}).get(
            self.title, {}
        )

    @contextmanager
    def session(self):
        with ui.card_section().classes("w-full"):
            yield

    def create_serie(self, name: str, type: str = "line"):
        serie = SerieData(name=name, type=type, data=[0])
        self._series.append(serie)

    def get_serie(self,name:str):
        for serie in self._series:
            if serie.name == name:
                return serie

    async def sample(self, serialno: str, app: str, process: str):
        raise NotImplementedError

    def update_chart(self):
        options = self.chart.options
        options.update(
            {
                "series": Series(self._series).model_dump(),
            }
        )
        options["dataZoom"][0].update(self.dataZoom)
        options["legend"]["selected"].update(self.legend_selected)
        self.chart.update()
        self._create_aggregate.refresh()

    def add_point(self, serie_name: str, value: float, type: str = "line"):
        if serie_name not in [serie.name for serie in self._series]:
            self.create_serie(serie_name, type)

        for serie in self._series:
            if serie.name == serie_name:
                serie.data.append(value)
                return

    def _handle_datazoom(self, event: GenericEventArguments):
        app.storage.general["android_profiler_datazoom"] = event.args

    def _handle_legendselectchanged(self, event: GenericEventArguments):
        app.storage.general["android_profiler_legend"][self.title] = event.args[
            "selected"
        ]

    @ui.refreshable
    def _create_aggregate(self):
        
        aggregates = []

        for serie in self._series:
            if not serie.data:
                average = 0
                min_value = 0
                max_value = 0
            else:
                average = round(sum(serie.data) / len(serie.data),2)
                min_value = round(min(serie.data),2)
                max_value = round(max(serie.data),2)
                
            aggregates.append({
                "name": serie.name,
                "max": f"{max_value}{self._y_unit}",
                "min": f"{min_value}{self._y_unit}",
                "average": f"{average}{self._y_unit}",
            })
        
        ui.table(rows=aggregates).classes("w-full")


    def clear(self):
        for serie in self._series:
            serie.data.clear()
        self.update_chart()
