##
## Very simple internal cache
##
import time

class Cache:
    def __init__(self, ctx):
        self.ctx = ctx
        try:
            self.expire = int(self.ctx.cfg["cache/expire"])
        except:
            self.expire = 300
        self.cache = {}
    def __setitem__(self, key, val):
        self.cache[key] = (time.time(), val)
    def __getitem__(self, key):
        if not self.cache.has_key(key):
            return None
        stamp, val = self.cache[key]
        if time.time() - stamp > self.expire:
            del self.cache[key]
            return None
        return val