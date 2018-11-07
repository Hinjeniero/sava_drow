import time
__all__ = ["time_it", "run_async"]

#Decorator to check time of execution in each function
def time_it(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        print(function.__name__+" execution time was "+str((time.time()-start)*1000)+" ms")
        return result
    return wrapper
 
def run_async(function):
    from threading import Thread
    def wrapper(*args, **kwargs):
        func_thr = Thread(name=function.__name__, target=function, args=args, kwargs=kwargs)
        func_thr.start()
        return func_thr
    return wrapper