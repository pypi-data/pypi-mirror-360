import redis
import logging


logger = logging.getLogger(__name__)


def catchAttr(func):
    def wrapper(self, *args, **kargs):
        try:
            return func(self, *args, **kargs)
        except(AssertionError, AttributeError):
            raise
        except:
            return object.__getattribute__(self.conn, args[0])
    return wrapper


class OPRedis:

    def __init__(self, host=None, port=None, passwd=None, startup_nodes=None, max_connections=2000):
        if startup_nodes:
            from rediscluster import RedisCluster, ClusterBlockingConnectionPool
            pool = ClusterBlockingConnectionPool(
                startup_nodes=startup_nodes, skip_full_coverage_check=True,
                password=passwd, max_connections=max_connections, decode_responses=True)
            self.conn = RedisCluster(connection_pool=pool)
        else:
            pool = redis.ConnectionPool(host=host, port=port,
                                        max_connections=max_connections, db=0, decode_responses=True)
            self.conn = redis.StrictRedis(connection_pool=pool, password=passwd,
                                          decode_responses=True)

    @catchAttr
    def __getattr__(self, attr):
        method = object.__getattribute__(self.conn, attr)
        if method:
            if hasattr(method, '__call__'):
                return self._catchExcept(method)
            return method
        else:
            raise AttributeError("redis not this attr")

    def _catchExcept(self, func):
        '''deal callable exception'''
        def wrapper(*args, **kargs):
            try:
                return func(*args, **kargs)
            except:
                try:
                    method = object.__getattribute__(self.conn, func.__name__)
                    return method(*args, **kargs)
                except:
                    raise
        return wrapper
