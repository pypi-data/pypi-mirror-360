import datetime
import json
import logging
import logging.handlers
import os
import shutil
from .android_profiler_service import AndroidProfielerService


class JsonFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, ensure_ascii=False)
        return super().format(record)


class _RecordService:
    @property
    def logger(self):
        return self._logger

    def _setup_logger(self):
        self._file_handler = logging.FileHandler(
            "record.log", mode="w", delay=True, encoding="utf-8"
        )
        self._file_handler.setFormatter(JsonFormatter())

        self._logger = logging.getLogger("RecordService")
        self._logger.addHandler(logging.StreamHandler())
        self._logger.addHandler(self._file_handler)
        self._logger.setLevel(logging.INFO)

    def _release_logger(self):
        self._logger.removeHandler(self._file_handler)
        self._file_handler.flush()
        self._file_handler.close()

    async def init_logger(self, serialno: str, app: str, process: str):
        device = await AndroidProfielerService.get_device(serialno)
        model_name = await device.prop.get("ro.product.model")

        self._setup_logger()

        app_info = await AndroidProfielerService.get_app_info(serialno, app)
        self.logger.info(
            {
                "model": model_name,
                "platform": "android",
                "app": app,
                "process": process,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **app_info,
            }
        )
        device_info = await AndroidProfielerService.get_device_info(serialno)
        self.logger.info(device_info)

    def save_record(self, filename: str):
        self._release_logger()
        if os.path.exists("record.log"):
            if not os.path.exists("records"):
                os.makedirs("records")
            shutil.move("record.log", f"records/{filename}.pcat")

    def record_files(self):
        if not os.path.exists("records"):
            os.makedirs("records")

        files = os.listdir("records")
        return [f for f in files if f.endswith(".pcat")]


RecordService = _RecordService()
