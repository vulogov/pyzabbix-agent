##
## Python-Zabbix cache 
##
import redis
try:
    import cPickle as pickle
except:
    import pickle

class Cache:
    def __init__(self, ctx):
        self.ctx = ctx
        try:
            self.expire = int(self.ctx.cfg["cache/expire"])
        except:
            self.expire = 300
        try:
            self.cache = redis.StrictRedis(host=self.ctx.cfg["redis/server"], port=6379, db=0)
            self.ready = True
        except KeyboardInterrupt:            
            self.ready = False
    def __setitem__(self, key, val):
        self.cache.set(key, pickle.dumps(val))
        self.cache.expire(key, self.expire)
    def __getitem__(self, key):
        if not self.cache.exists(key):
            return None
        val = pickle.loads(self.cache.get(key))
        return val
