""""helper functions for testing"""

from multiprocessing import Process, Manager
import time


def async_apply(ret, f, *args, **kwargs):
    """
    @param ret list created by multiprocessing.Manager.list()
    @param f function
    @param args arguments for function f
    """
    ret.append(f(*args, **kwargs))


def exec_concurrent(func1, func2):
    """
    Execute two functions concurrently.
    'func2' is executed in the another process.
    """
    manager = Manager()
    ret = manager.list()

    p = Process(target=async_apply, args=(ret, func2))
    p.start()
    ret1 = func1()
    p.join()

    return ret1, ret[0]


def exec_before(func, func_before, *args, **kwargs):
    """
    Execute the function 'func_before' with arguments, then return the result of the partial function 'func'.
    """
    def f():
        func_before(*args, **kwargs)
        return func()
    return f


def a_after_b(func_a, func_b):
    """Execute 'func_b', await a moment, then execute 'func_a'."""
    return exec_concurrent(exec_before(func_a, time.sleep, 0.1), func_b)


def a_before_b(func_a, func_b):
    """Execute 'func_a', await a moment, then execute 'func_b'."""
    return exec_concurrent(func_a, exec_before(func_b, time.sleep, 0.1))


if __name__ == '__main__':
    pass