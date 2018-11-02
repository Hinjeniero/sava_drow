import time

#Decorator to check time of execution in each function
def time_it(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        print(function.__name__+" execution time was "+str((time.time()-start)*1000)+" ms")
        return result
    return wrapper