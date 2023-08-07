import sys
from loguru import logger as preconfig_logger
from loguru._handler import Message

# from datetime import datetime
# from traceback import format_exc
from json import dumps as json_dumps

"""
class Record(TypedDict):
    elapsed: timedelta
    exception: Optional[RecordException]
    extra: Dict[Any, Any]
    file: RecordFile
    function: str
    level: RecordLevel
    line: int
    message: str
    module: str
    name: Union[str, None]
    process: RecordProcess
    thread: RecordThread
    time: datetime
"""
from pathlib import Path


def monitor_race_condition(local_file: Path, remote_file: Path):
    from datetime import datetime

    name_mapping = {
        "last_access": "st_atime",
        "last_modified": "st_mtime",
        "last_status_change": "st_ctime",
    }

    local_stat = local_file.stat()
    remote_stat = remote_file.stat()
    local_time = {
        time_field: datetime.fromtimestamp(
            getattr(local_stat, name_mapping[time_field])
        )
        for time_field in name_mapping
    }
    remote_time = {
        time_field: datetime.fromtimestamp(
            getattr(remote_stat, name_mapping[time_field])
        )
        for time_field in name_mapping
    }

    log = f"timefiled: {local_time=}, {remote_time=}"
    logger.info(log)


class OnesyncRecord(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_record(cls, record: dict):
        record_time = record["time"].replace(tzinfo=None)
        str_time = record_time.strftime("%Y-%m-%d %H:%M:%S")

        custom_record = {
            "level": record["level"].name,
            "message": record["message"],
            "file": record["file"].path,
            "line": record["line"],
            "process_name": record["process"].name,
            "process_id": record["process"].id,
            "datetime": str_time,
            "function": record["function"],
            "timestamp": record_time.timestamp(),
            "exception": None,
            **record["extra"],
        }

        obj = cls(**custom_record)
        return obj

    def dumps(self):
        return json_dumps(self)


def shell_sink(message: Message):
    json_record = OnesyncRecord.from_record(message.record).dumps()
    print(json_record)



preconfig_logger.remove(0)

preconfig_logger.add(
    sys.stderr,
    format="<green>{time:MM-DD HH:mm:ss}</green> | "
    # "<R><k>{process.name}-{process.id}</k></R> | "
    "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>",
)

logger = preconfig_logger
# logger.add(sink=shell_sink, colorize=True, enqueue=True)  # type: ignore
