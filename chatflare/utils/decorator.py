import warnings 
from functools import wraps 


def test_only(func):
    def wrapper(*args, **kwargs): 
        warnings.warn("This function is for testing purposes only")
        return func(*args, **kwargs)
    return wrapper 

def deprecated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(f"{func.__name__} is deprecated and may be removed in future versions.", DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    return wrapper