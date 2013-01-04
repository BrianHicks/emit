'test for multilang'
import sys
import msgpack

message = msgpack.unpackb(sys.stdin.read())

for i in range(message['count']):
    sys.stdout.write(msgpack.packb(i) + '\n')
