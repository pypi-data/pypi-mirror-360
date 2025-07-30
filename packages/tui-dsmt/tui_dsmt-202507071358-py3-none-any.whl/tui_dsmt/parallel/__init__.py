import logging
from typing import Callable

import ipyparallel as ipp

from .MapReduce import MapReduce
from .Pregel import Pregel


def mpi_run(fun: Callable, num_proc: int = 3):
    with ipp.Cluster(engines='mpi', n=num_proc, log_level=logging.ERROR) as rc:
        view = rc.broadcast_view()
        result = view.apply_sync(fun)
        return result
