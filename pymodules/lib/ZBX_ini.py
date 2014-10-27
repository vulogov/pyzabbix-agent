##
## Handling of the Python-Zabbix agent module configuration file
##
import posixpath
import ConfigParser

class ZBX_ini:
    def __init__(self, ctx):
        self.ctx = ctx
        self.cfg_filename = "%s/pyzabbix.ini"%self.ctx.cfg_path
        try:
            self.cfg = ConfigParser.SafeConfigParser(allow_no_value=True)
            self.cfg.readfp(open(self.cfg_filename))
        except:
            self.cfg = None
    def __getitem__(self, key):
        if not self.cfg:
            return None
        p = key.split("/")
        if len(p) == 1:
            try:
                return self.cfg.get("main", p[0])
            except:
                return None
        elif len(p) >= 2:
            try:
                return self.cfg.get(p[0], p[1])
            except:
                return None
        else:
            return None

        