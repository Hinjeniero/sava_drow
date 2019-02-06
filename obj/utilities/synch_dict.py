"""--------------------------------------------
synch_dict module. Contains a thread-safe implementation of a python dictionary.
Have the following classes:
    Resizer
--------------------------------------------"""
__all__ = ['Dictionary']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

#Python libraries
import time
from wrapt import synchronized

class Dictionary:
    """Dictionary class. Thread-safe implementation of dict,
    achieved through the use of the decorator wrapt.synchronized.
    Attributes:
        dict (dict):    A python basic dictionary.
        is_empty (boolean): True if the dictionary doesn't contain any element.
    """
    
    def __init__(self, exceptions=False):
        """Dictionary constructor."""
        self.dict = {}
        self.is_empty = True
        self.exceptions = exceptions

    @synchronized
    def get_item(self, key):
        """Gets an item from the dict if the key is found in it.
        Args:
            key (any):  Key to search for in the dictionary.
        Returns
            (any||None):Returns the associated element if the key is found in the dictionary.
                        Returns None if the key isn't in the dict."""
        try:
            return self.dict[key]
        except KeyError:
            if self.exceptions:
                raise KeyError
            return None

    @synchronized
    def add_item(self, key, item):
        """Adds an item associated with a key to the dictionary.
        Args:
            key (any):  Key to set in the dictionary.
            item (any): Item to associate to key set in the dictionary."""
        self.dict[key]= item
        self.is_empty = False

    @synchronized
    def delete_item(self, key):
        """Deletes and returns the associated item from the dict if the key is found in it.
        Args:
            key (any):  Key to search for in the dictionary.
        Returns:
            (any):  Deleted element."""
        self.is_empty = True if len(self.dict) is 1 else False
        return self.dict.pop(key)

    @synchronized
    def keys(self):
        return self.dict.keys()

    @synchronized
    def items(self):
        return self.dict.items()

    @synchronized
    def values(self):
        return self.dict.values()
    @synchronized
    def values_list(self):
        return list(self.dict.values())

    @synchronized
    def clear(self):
        self.dict.clear()