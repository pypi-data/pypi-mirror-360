import os
import time

import autoregistry

type TimerName = str


_get_time = autoregistry.Registry()
_get_time["children_system"] = lambda: os.times().children_system
_get_time["children_user"] = lambda: os.times().children_user
_get_time["elapsed"] = lambda: os.times().elapsed
_get_time["monotonic"] = time.monotonic
_get_time["perf"] = time.perf_counter
_get_time["process"] = time.process_time
_get_time["system"] = lambda: os.times().system
_get_time["thread"] = time.thread_time
_get_time["time"] = time.time
_get_time["user"] = lambda: os.times().user


def get_time(timer: TimerName = "perf") -> float:
    return _get_time[timer]()
