'simple rq app'
from redis import Redis
from emit.router.rq import RQRouter

import logging

router = RQRouter(redis_connection=Redis(), node_modules=['tasks'])

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
