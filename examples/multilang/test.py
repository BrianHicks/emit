'test for multilang'
import sys
import json

message = json.loads(sys.stdin.read())

for i in range(message['count']):
    sys.stdout.write(json.dumps(i) + '\n')
