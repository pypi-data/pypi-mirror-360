from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService


class TemperatureMonitorCard(MonitorCard):
    title = "Temperature"
    description = "设备温度情况"

    def __init__(
        self,
        y_axis_unit: str = "℃",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )
        self.create_serie("CPU温度")
        self.create_serie("GPU温度")
        self.create_serie("体感温度")
        self.create_serie("电池温度")
        self.update_chart()

    async def sample(self, serialno: str, app: str, process: str):
        device = await AndroidProfielerService.get_device(serialno)

        stat = await device.temp.stat()
        cpu_temp = round(stat.cpu, 2)
        gpu_temp = round(stat.gpu, 2)
        skin_temp = round(stat.skin, 2)
        battery_temp = round(stat.battery, 2)

        self.add_point("CPU温度", cpu_temp)
        self.add_point("GPU温度", gpu_temp)
        self.add_point("体感温度", skin_temp)
        self.add_point("电池温度", battery_temp)
        RecordService.logger.info(
            {
                "name": self.title,
                "CPU温度": cpu_temp,
                "GPU温度": gpu_temp,
                "体感温度": skin_temp,
                "电池温度": battery_temp,
            }
        )
        self.update_chart()
