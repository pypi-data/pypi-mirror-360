import time
from functools import wraps
from pprint import pprint


class Timer:
    def __init__(self, title:str = None,save_time_list: list[float] = None):
        self.title = title
        self.save_time_list = save_time_list

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            start_time = time.perf_counter()
            ret = func(*args, **kwargs)
            cost_time = time.perf_counter() - start_time

            if self.save_time_list:
                self.save_time_list.append(cost_time)
            if self.title:
                if cost_time > 3600:
                    print(f"{self.title}耗时: {cost_time/3600:.4f}h")
                elif cost_time > 60:
                    print(f"{self.title}耗时: {cost_time/60:.4f}min")
                else:
                    print(f"{self.title}耗时: {cost_time:.4f}s")

            return ret

        return decorated


def timer(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        start_time = time.perf_counter()
        res = func(*args, **kwargs)
        cost_time = time.perf_counter() - start_time
        print(f"{func.__name__} cost time: {cost_time:.4f}s")
        return res

    return decorated


def test_timer():
    save = []

    @Timer(save)
    def do_something():
        time.sleep(1)

    do_something()
    pprint(save)


def test_timer1():
    @timer
    def do_something():
        time.sleep(1)

    do_something()
