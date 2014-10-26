##
## Zabbix-Python startup procedures
##


import imp
from ZBX_ini import ZBX_ini


class ZBX_Context:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path
        self.cfg      = ZBX_ini(self)
        self.name = self.cfg["name"].lower()
        if not self.name or self.name == "hostname":
            import socket
            self.name = socket.gethostname().lower()
        self.initCache()
        self.initAgents()
    def initCache(self):
        self.cache = None
        ctype = self.cfg["cache/type"]
        if not ctype:
            ctype="internal"
        c = self.getFromModule("ZBX_cache_%s"%ctype, "Cache")
        if c != None:
            self.cache = c(self)
        if not self.cache.ready:
            ## If cache is not ready, we do not have any cache
            self.cache = None
    def initAgents(self):
        self.agents = {}
        agents = self.cfg["agents/agents"]
        if agents:
            agent = agents.split(",")
            for a in agent:
                _a = a.strip().lower()
                m = "ZBX_agent_%s"%_a
                c = self.getFromModule(m, "Agent")
                if not c:
                    continue
                self.agents[_a] = c(self)
                print "Agent %s installed:"%_a,self.agents[_a].desc()
    def getFromModule(self, modname, attrname):
        fp, pathname, description = imp.find_module(modname)
        try:
            mod = imp.load_module(modname, fp, pathname, description)
        except:
            return None
        finally:
            fp.close()
        try:
            return getattr(mod, attrname)
        except:
            return None

    def Agent(self, name, _class):
        self.agents[name] = _class(ctx)

def main(cfg_path):
    print "Python-Zabbix extention is initialized"
    return ZBX_Context(cfg_path)
