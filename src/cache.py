from utils import *
from settings import *

__all__ = [
    'Cache',
]

class Cache:
    def __init__(self):
        self.data = {}

    def add(self, tag, f, hard=False):
        if hard or tag not in self.data:
            self.data[tag] = f()
            logger.log('Cache: calling f()')

    def rem(self, tag):
        del self.data[tag]

    def get(self, tag, f=None):
        if tag not in self.data:
            if f is None:
                raise Exception('cache.py Cache.get f==None')
                return None
            self.data[tag] = f()
        return self.data[tag]
