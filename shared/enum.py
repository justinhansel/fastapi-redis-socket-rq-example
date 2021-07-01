from enum import Enum


class RedisChannel(Enum):
    WORKER = 1
    FRONTEND = 2


class JobType(Enum):
    BASIC = 1
    BASIC_ARG = 2
    DATABASE = 3


class JobStatus(Enum):
    STARTED = 1
    COMPLETE = 2


worker_channel = f"channel{RedisChannel.WORKER}"

