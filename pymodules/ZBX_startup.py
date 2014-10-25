class ZBX_Context:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path

def main(cfg_path):
    print "Python-Zabbix extention is initialized"
    return ZBX_Context(cfg_path)
