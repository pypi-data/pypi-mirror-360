from collections import defaultdict
import json
import os
from nicegui import ui
from perfcat.components.layout import Page, Header
from perfcat.components.monitors import monitor_factory_map
from perfcat.components.profiler import MonitorCard


class ReportPage(Page):
    def __init__(self) -> None:
        @ui.page("/home/report", title="性能报告")
        async def _(filename: str):
            # await self._frame()
            await self.render(filename)

    async def render(self, filename: str):
        Header()

        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
            base_info = json.loads(lines[0])
            device_info = json.loads(lines[1])

        with ui.card().classes("w-full"):
            ui.label(f"{base_info['platform'].capitalize()}性能报告").classes(
                "text-2xl font-bold"
            )
            columns = [
                {
                    "name": "name",
                    "label": "名称",
                    "field": "name",
                    "required": True,
                    "align": "left",
                },
                {
                    "name": "value",
                    "label": "值",
                    "field": "value",
                    "required": True,
                    "align": "right",
                    "style": "overflow-wrap:anywhere",
                },
            ]
            rows = [
                {"name": "测试设备", "value": base_info.get("model", "unknown")},
                {"name": "包名", "value": base_info.get("app", "unknown")},
                {"name": "进程名", "value": base_info.get("process", "unknown")},
                {"name": "构建版本", "value": base_info.get("version", "unknown")},
                {"name": "安装日期", "value": base_info.get("install_time", "unknown")},
                {"name": "测试时间", "value": base_info.get("created_at", "unknown")},
            ]
            ui.label("基本信息")
            ui.table(columns=columns, rows=rows).classes("w-full").props(
                "hide-header dense"
            )

            ui.label("设备信息")
            rows = [{"name": key, "value": value} for key, value in device_info.items()]
            ui.table(columns=columns, rows=rows).classes("w-full").props(
                "hide-header dense"
            )

            monitor_seires: dict[str, list] = defaultdict(list) 

            for line in lines[2:]:
                data: dict = json.loads(line)
                title = data["name"]
                monitor_seires[title].append(data)
               
            for moinitor_name,monitor_class in monitor_factory_map.items():
                if moinitor_name in monitor_seires:
                    monitor = monitor_class(show_aggregate=True)
                    monitor.clear()
                    for data in monitor_seires[moinitor_name]:
                        for serie_name, data_value in data.items():
                            if serie_name != "name":
                                monitor.add_point(serie_name, data_value)
                    monitor.update_chart()


ReportPage()
