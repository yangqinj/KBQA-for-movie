"""
@author: Qinjuan Yang
@time: 2022-02-10 20:27
@desc: 
"""
from functools import wraps


def print_func_name(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        print("function", func.__name__, "is called.")
        return func(*args, **kwargs)
    return wrapped_function

