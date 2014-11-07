import imp
import traceback
import posixpath
try:
    import cPickle as pickle
except:
    import pickle

def main(ctx, cmd, *args):
    if ctx.cache:
        ## Check the cache first
        ret = ctx.cache["%s/%s"%(ctx.name, cmd)]
        if ret:
            return (1, ret, None)
    p_cmd = cmd.split(".")
    name = p_cmd[0]
    try:
        method = p_cmd[1]
    except:
        method = "main"
    params = p_cmd[2:]
    if ctx.agents.has_key(name):
        ## Try pre-spawned agent
        try:
            ret = apply(getattr(ctx.agents[name], method), (ctx,)+args)
            if ctx.cache:
                ctx.cache["%s/%s"%(ctx.name, cmd)] = ret
            return (1,ret,None)
        except:
            return (0,"Python agent trew traceback",traceback.format_exc())
    elif ctx.redis_queue and (ctx.redis_queue.exists("%s/%s"%(ctx.name, cmd)) or ctx.redis_queue.exists(cmd) or "%s/%s"%(ctx.name, cmd) in ctx.redis_queues or (cmd in ctx.redis_queues)):
        ## Try Redis queue
        try:
            ret = None
            for qname in ["%s/%s"%(ctx.name, cmd), cmd]:
                ret = ctx.redis_queue.lpop(qname)
                if ret:
                    break
            if not ret:
                return (0, ret, "No data from Redis")
            else:
                return (1, pickle.loads(ret), None)
        except:
            return (0, ret, "No data from Redis")
    else:
        try:
            fp, pathname, description = imp.find_module(name)
            if posixpath.dirname(pathname).split("/")[-1] != "pymodules":
                ## If discovered module isn't in pymodules, we don't want to call it
                raise ImportError, name
        except:
            return (0,"Python module not exists",traceback.format_exc())
        try:
            mod = imp.load_module(name, fp, pathname, description)
        except:
            return (0,"Python module can not be loaded",traceback.format_exc())
        finally:
            fp.close()
        try:
            ret = apply(getattr(mod, method), (ctx,)+args)
            if ctx.cache:
                ctx.cache["%s/%s"%(ctx.name, cmd)] = ret
        except:
            return (0,"Python module threw traceback",traceback.format_exc())
        return (1, ret, None)
