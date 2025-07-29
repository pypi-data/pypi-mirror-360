from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService


class FPSMonitorCard(MonitorCard):
    title = "FPS(Game)"
    description = "游戏帧率(无法采集原生APP帧率)"

    def __init__(
        self,
        y_axis_unit: str = "",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )

        self.create_serie("FPS")
        self.create_serie("Jank", type="bar")
        self.create_serie("Big-Jank", type="bar")
        self.update_chart()

    async def sample(self, serialno: str, app: str, process: str):
        device = await AndroidProfielerService.get_device(serialno)
        stat = await device.fps.stat(process)
        fps = round(stat.fps, 2)

        self.add_point("FPS", fps)
        self.add_point("Jank", stat.jank)
        self.add_point("Big-Jank", stat.big_jank)
        RecordService.logger.info(
            {
                "name": self.title,
                "FPS": fps,
                "Jank": stat.jank,
                "Big-Jank": stat.big_jank,
            }
        )
        self.update_chart()
