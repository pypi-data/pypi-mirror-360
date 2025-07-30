from dataclasses import dataclass, field
import datetime
from enum import Enum

from lib import get_uuid


class TaskStatus(Enum):
    FAILED = -1  # 失败
    SUCCEEDED = 0  # 成功
    PENDING = 1  # 等待
    RUNNING = 2  # 运行
    CANCELLED = 3  # 取消
    RETRYING = 4  # 重试
    TIMEOUT = 5  # 超时


@dataclass
class TaskId:
    tid: str = field(default_factory=get_uuid())
    timestamp: int = field(default=int(datetime.datetime.now().timestamp()))
    status: int = field(default=1)
    args: dict = field(default_factory=dict)
