from enum import Enum


class TaskStatus(Enum):
    FAILED = -1  # 失败
    SUCCEEDED = 0  # 成功
    PENDING = 1  # 等待
    RUNNING = 2  # 运行
    CANCELLED = 3  # 取消
    RETRYING = 4  # 重试
    TIMEOUT = 5  # 超时
