#!python3
#coding:utf-8

import time
from wrapt import synchronized
__author__ = 'David Flaity Pardo'

class Dictionary:
    def __init__(self):
        self.dict = {}
        self.is_empty = True

    @synchronized
    def get_item(self, key):
        try:
            return self.dict[key]
        except KeyError:
            return None

    @synchronized
    def add_item(self, key, item):
        self.dict[key]= item
        self.is_empty = False

    @synchronized
    def delete_item(self, key):
        self.is_empty = True if len(self.dict) is 1 else False
        return self.dict.pop(key)
