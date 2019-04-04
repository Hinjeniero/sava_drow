"""--------------------------------------------
decorators module. Contains all the decorators used in this workspace.
Also added a pool-manager of threads
--------------------------------------------"""

__all__ = ['time_it', 'run_async']
__version__ = '0.3'
__author__ = 'David Flaity Pardo'
import threading
from settings import PARAMS
from wrapt import synchronized

THREAD_POOL = []
THREAD_BUSY = {}
TASK_POOL = []
TASK_POOL_EMPTY = threading.Condition()
END = False

def END_ALL_THREADS():
    for _ in range(0, PARAMS.NUM_THREADS):
        TASK_POOL.append('END')
    TASK_POOL_EMPTY.acquire()
    TASK_POOL_EMPTY.notifyAll()
    TASK_POOL_EMPTY.release()

def active_thread():
    while True:
        TASK_POOL_EMPTY.acquire()
        while len(TASK_POOL)==0:
            TASK_POOL_EMPTY.wait()
        data = TASK_POOL.pop(0)
        TASK_POOL_EMPTY.release()
        if data == 'END':
            return
        method_with_event(data[0], data[1], data[2], data[3])

for i in range(0, PARAMS.NUM_THREADS):
    thread_name = "subthread_"+str(i)
    THREAD_POOL.append(threading.Thread(name=thread_name, target=active_thread))
    THREAD_BUSY[thread_name] = False
    THREAD_POOL[i].start()

def method_with_event(end_event, function, args, kwargs):
    #print("START OF "+function.__name__)
    if threading.current_thread() is not threading.main_thread():   
        THREAD_BUSY[threading.currentThread().getName()] = True
    function(*args, **kwargs)
    end_event.set()
    if threading.current_thread() is not threading.main_thread():
        THREAD_BUSY[threading.currentThread().getName()] = False
    #print("END OF "+function.__name__)

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
    def wrapper(*args, **kwargs):
        end_event = threading.Event()
        #print("ADDED FUNCTION "+function.__name__)
        #print(THREAD_BUSY.values())
        if all(busy for busy in THREAD_BUSY.values()):
            #print("ALL THREADS BUSY!, executing "+function.__name__)
            method_with_event(end_event, function, args, kwargs)
        else:
            TASK_POOL_EMPTY.acquire()
            TASK_POOL.append((end_event, function, args, kwargs))
            TASK_POOL_EMPTY.notify()
            TASK_POOL_EMPTY.release()
        return end_event
    return wrapper
    
def run_async_not_pooled(function):
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
