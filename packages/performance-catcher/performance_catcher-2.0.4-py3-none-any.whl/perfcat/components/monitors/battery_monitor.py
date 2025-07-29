"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2025-06-29 20:12:56
Copyright © Kaluluosi All rights reserved
"""

from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService


class BatteryLevelMonitorCard(MonitorCard):
    title = "Battery(Level)"
    description = "电量百分比"

    def __init__(
        self,
        y_axis_unit: str = "%",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )

        self.create_serie("level")
        self.update_chart()

    async def sample(self, serialno: str, app: str, process: str):
        dev = await AndroidProfielerService.get_device(serialno)

        battery_stat = await dev.battery.stat()
        level = battery_stat.level
        self.add_point("level", level)

        RecordService.logger.info({"name": self.title, "level": level})
        self.update_chart()


class BatterymAhMonitorCard(MonitorCard):
    title = "Battery(mAh)"
    description = "电池电量mAh容量(毫安时)"

    def __init__(
        self,
        y_axis_unit: str = "mAh",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )
        self.create_serie("mAh")
        self.update_chart()

    async def sample(self, serialno: str, app: str, process: str):
        dev = await AndroidProfielerService.get_device(serialno)

        battery_stat = await dev.battery.stat()
        mAh = battery_stat.charge_counter / 1000
        self.add_point("mAh", mAh)
        RecordService.logger.info({"name": self.title, "mAh": mAh})
        self.update_chart()
