"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2025-07-04 00:15:39
Copyright © Kaluluosi All rights reserved
"""

from perfcat.components.profiler import MonitorCard
from .cpu_monitor import CPUMonitorCard
from .memery_monitor import MemoryTotalPSSMonitorCard
from .battery_monitor import BatteryLevelMonitorCard, BatterymAhMonitorCard
from .fps_monitor import FPSMonitorCard
from .temperature_monitor import TemperatureMonitorCard
from .traffic_monitor import TrafficMonitorCard

__all__ = [
    "FPSMonitorCard",
    "CPUMonitorCard",
    "MemoryTotalPSSMonitorCard",
    "TemperatureMonitorCard",
    "BatteryLevelMonitorCard",
    "BatterymAhMonitorCard",
    "TrafficMonitorCard",
]

monitor_factory_map: dict[str, type[MonitorCard]] = {
    FPSMonitorCard.title: FPSMonitorCard,
    CPUMonitorCard.title: CPUMonitorCard,
    MemoryTotalPSSMonitorCard.title: MemoryTotalPSSMonitorCard,
    BatteryLevelMonitorCard.title: BatteryLevelMonitorCard,
    BatterymAhMonitorCard.title: BatterymAhMonitorCard,
    TemperatureMonitorCard.title: TemperatureMonitorCard,
    TrafficMonitorCard.title: TrafficMonitorCard,
}
