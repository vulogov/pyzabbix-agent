import imp

def main(ctx, cmd, *args):
    p_cmd = cmd.split(".")
    name = p_cmd[0]
    try:
        method = p_cmd[1]
    except:
        method = "main"
    params = p_cmd[2:]
    if ctx.agents.has_key(name):
        try:
            ret = apply(getattr(ctx.agents[name], method), (ctx,)+args)
        except:
            return (0,"Python agent trew traceback",traceback.format_exc())
    else:
        fp, pathname, description = imp.find_module(name)
        try:
            mod = imp.load_module(name, fp, pathname, description)
        except:
            return (0,"Python module can not be loaded",traceback.format_exc())
        finally:
            fp.close()
        try:
            ret = apply(getattr(mod, method), (ctx,)+args)
        except:
            return (0,"Python module threw traceback",traceback.format_exc())
        return (1, ret, None)
