#   Narvi - a simple python web application server
#
#   Copyright (C) 2022-2025 Visual Topology Ltd
#
#   Licensed under the Open Software License version 3.0
import os
import subprocess
import sys

import threading
import asyncio

from hyrrokkin_engine_drivers.execution_worker import ExecutionWorker

class ThreadRunner(threading.Thread):

    def __init__(self, host_name, port, verbose=False):
        super().__init__(daemon=True)
        self.host_name = host_name
        self.port = port
        self.worker = ExecutionWorker(host_name,port,verbose)

    def run(self):
        asyncio.run(self.worker.run())

    def get_pid(self):
        return os.getpid()

    def stop(self, hard=False):
        raise Exception("stop not supported")

    def get_return_code(self):
        return 0


