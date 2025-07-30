import threading


class Singleton:
    _lock = threading.Lock()  # 创建一个类级别的锁

    def __init__(self, cls):
        self._cls = cls
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            with self._lock:  # 使用锁保护实例化代码
                if self._instance is None:  # 再次检查实例是否已经被创建
                    self._instance = self._cls(*args, **kwargs)
        return self._instance
