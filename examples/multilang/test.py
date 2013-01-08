'test for multilang'
import sys
try:
    import msgpack
except ImportError:
    import msgpack_pure as msgpack

message = msgpack.unpackb(sys.stdin.read())

for i in range(message['count']):
    sys.stdout.write(msgpack.packb(i) + '\n')
