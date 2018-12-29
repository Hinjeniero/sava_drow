"""--------------------------------------------
decorators module. Contains all the decorators used in this workspace.
--------------------------------------------"""

__all__ = ['time_it', 'run_async']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

#Decorator to check time of execution in each function
def time_it(function):
    import time
    """Times the input function and prints the result on screen. 
    The time library is needed.
    Args:
        function (function):    Function whose execution will be timed.
        *args (:list: arg):     Input arguments of the function.
        **kwargs (:dict: kwarg):Input keyword arguments of the function.
    Returns:
        (any):  Returns whatever the function itself returns."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        print(function.__name__+" execution time was "+str((time.time()-start)*1000)+" ms")
        return result
    return wrapper
 
def run_async(function):
    """Executes the function in a separate thread to avoid locking the main thread.
    The function result can't be returned normally, to request results, the function must
    insert them in a buffer of data passed as an input argument. 
    The Threading library is needed.
    Args:
        function (function):    Function whose execution will be timed.
        *args (:list: arg):     Input arguments of the function.
        **kwargs (:dict: kwarg):Input keyword arguments of the function.
    Returns:
        (Threading.thread):  Thread that is executing the function."""
    from threading import Thread
    def wrapper(*args, **kwargs):
        func_thr = Thread(name=function.__name__, target=function, args=args, kwargs=kwargs)
        func_thr.start()
        return func_thr
    return wrapper