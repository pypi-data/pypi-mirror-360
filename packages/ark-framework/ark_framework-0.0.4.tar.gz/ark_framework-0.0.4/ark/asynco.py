import functools
import queue
import threading
import traceback


class Worker(threading.Thread):

    def __init__(self, tasks):
        super().__init__(daemon=True)
        self.tasks = tasks
        self.start()

    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()
            finally:
                self.tasks.task_done()


class ThreadPool:

    def __init__(self, num_threads):
        self.tasks = queue.Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        self.tasks.join()

class Asynco:
    _instance = None
    pool = {}
    default_pool_size = 10

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Asynco, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def get_pool(self):
        return self.pool

    @staticmethod
    def get_default_pool_size():
        return Asynco.default_pool_size

    @staticmethod
    def get_object():
        if Asynco._instance:
            return Asynco._instance
        else:
            return Asynco()

    @staticmethod
    def create_pool(pool_name, size = default_pool_size):
        pool = Asynco.get_object().get_pool()
        if pool_name in pool:
            raise Exception(pool_name + ' already exists')
        else:
            pool[pool_name] =  ThreadPool(size)

    @staticmethod
    def complete_all_task(pool_name):
        asynco_object = Asynco.get_object()
        pool = asynco_object.get_pool()
        pool[pool_name].wait_completion()


def asynco(function=None, pool_name=None):
    from threading import Thread
    from functools import wraps
    if function is None:
        return functools.partial(asynco, pool_name=pool_name)
    @wraps(function)
    def wrapper(*args, **kwargs):
        asynco_object =  Asynco.get_object()
        pool = asynco_object.get_pool()
        if pool_name:
            lock = threading.RLock()
            with lock:
                if pool_name in pool:
                    pool[pool_name].add_task(function, *args, **kwargs)
                else:
                    pool[pool_name] = ThreadPool(asynco_object.get_default_pool_size())
                    pool[pool_name].add_task(function, *args, **kwargs)
        else:
            t1 = Thread(target=function, args=args, kwargs=kwargs)
            t1.start()
        return
    return wrapper





