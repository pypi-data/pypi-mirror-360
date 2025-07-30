import logging
from concurrent.futures import ThreadPoolExecutor
from icecream.utils.singleton import Singleton

logger = logging.getLogger(__name__)


@Singleton
class TaskPlatform:

    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=40)

    def get_queue_size(self):
        return self.pool._work_queue.qsize()

    def submit(self, func, *args, **kargs):
        self.pool.submit(func, *args, **kargs)

    def stop(self):
        self.pool.shutdown()
