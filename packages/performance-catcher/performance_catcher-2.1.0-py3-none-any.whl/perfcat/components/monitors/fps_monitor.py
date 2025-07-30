from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService
from nicegui import ui

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

        if self.show_aggregate:
            self._create_new()

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

    def update_chart(self):
        self._create_new.refresh()
        return super().update_chart()


    @ui.refreshable
    def _create_new(self):
        
        aggregate = []

        jank_serie = self.get_serie("Jank")

        if jank_serie and jank_serie.data:
            jank_count = len(list(filter(lambda x: x > 0, jank_serie.data)))
            total_count = len(jank_serie.data)
            jank_rate = round(jank_count / total_count * 100, 2)
            aggregate.append({
                "name": "Jank概率",
                "value": f"{jank_rate}%"
            })

        big_jank_serie = self.get_serie("Big-Jank")

        if big_jank_serie and big_jank_serie.data:
            big_jank_count = len(list(filter(lambda x: x > 0, big_jank_serie.data)))
            total_count = len(big_jank_serie.data)
            big_jank_rate = round(big_jank_count / total_count * 100, 2)
            aggregate.append({
                "name": "Big-Jank概率",
                "value": f"{big_jank_rate}%"
            })

        ui.table(rows=aggregate)