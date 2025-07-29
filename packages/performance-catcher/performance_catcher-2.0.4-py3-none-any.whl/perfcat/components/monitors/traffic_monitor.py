"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2025-06-29 20:48:00
Copyright © Kaluluosi All rights reserved
"""

from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService
from async_adbc.plugins.traffic import TrafficStat


class TrafficMonitorCard(MonitorCard):
    title = "Traffic"
    description = "累计流量数据"

    def __init__(
        self,
        y_axis_unit: str = "KB",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )

        self.create_serie("receive")
        self.create_serie("send")
        self.update_chart()

        self.last_stat: TrafficStat | None

    def clear(self):
        self.last_stat = None
        return super().clear()

    async def sample(self, serialno: str, app: str, process: str):
        dev = await AndroidProfielerService.get_device(serialno)
        app_stat = await dev.traffic.app_stat(app)

        if self.last_stat is None:
            self.last_stat = app_stat

        diff = app_stat - self.last_stat

        receive = round(diff.receive / 1024, 2)
        send = round(diff.send / 1024, 2)

        self.add_point("receive", receive)
        self.add_point("send", send)
        RecordService.logger.info(
            {"name": self.title, "receive": receive, "send": send}
        )
        self.update_chart()
