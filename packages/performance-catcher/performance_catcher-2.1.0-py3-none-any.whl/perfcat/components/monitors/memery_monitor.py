from perfcat.components.profiler import MonitorCard
from perfcat.services import AndroidProfielerService, RecordService


class MemoryTotalPSSMonitorCard(MonitorCard):
    title = "Memory(PSS)"
    description = "APP Total PSS内存情况"

    def __init__(
        self,
        y_axis_unit: str = "MB",
        group: str = "monitor",
        show_aggregate: bool = False,
    ) -> None:
        super().__init__(
            y_axis_unit=y_axis_unit, group=group, show_aggregate=show_aggregate
        )
        self.create_serie("pss")
        self.create_serie("private_dirty")
        self.create_serie("private_clean")
        self.create_serie("swapped_dirty")
        self.create_serie("heap_size")
        self.create_serie("heap_alloc")
        self.create_serie("heap_free")

        self.update_chart()

    async def sample(self, serialno: str, app: str, process: str):
        device = await AndroidProfielerService.get_device(serialno)
        app_memory_stat = await device.mem.stat(process)

        pss = round(app_memory_stat.pss / 1000, 2)
        private_dirty = round(app_memory_stat.private_dirty / 1000, 2)
        private_clean = round(app_memory_stat.private_clean / 1000, 2)
        swapped_dirty = round(app_memory_stat.swapped_dirty / 1000, 2)
        heap_size = round(app_memory_stat.heap_size / 1000, 2)
        heap_alloc = round(app_memory_stat.heap_alloc / 1000, 2)
        heap_free = round(app_memory_stat.heap_free / 1000, 2)

        self.add_point("pss", pss)
        self.add_point("private_dirty", private_dirty)
        self.add_point("private_clean", private_clean)
        self.add_point("swapped_dirty", swapped_dirty)
        self.add_point("heap_size", heap_size)
        self.add_point("heap_alloc", heap_alloc)
        self.add_point("heap_free", heap_free)
        RecordService.logger.info(
            {
                "name": self.title,
                "pss": pss,
                "private_dirty": private_dirty,
                "private_clean": private_clean,
                "swapped_dirty": swapped_dirty,
                "heap_size": heap_size,
                "heap_alloc": heap_alloc,
                "heap_free": heap_free,
            }
        )
        self.update_chart()
