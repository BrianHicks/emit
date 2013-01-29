#!/usr/bin/env python
import sys
import rq

# Preload libraries
from app import router
router.resolve_node_modules()

# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with rq.Connection():
    qs = map(rq.Queue, sys.argv[1:]) or [rq.Queue()]

    w = rq.Worker(qs)
    w.work()
