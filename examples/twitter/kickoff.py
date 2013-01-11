import json
import os
import requests

from app import router

twitter = requests.get(
    'https://stream.twitter.com/1.1/statuses/sample.json',
    auth=(os.environ['EMIT_USERNAME'], os.environ['EMIT_PASSWORD']),
    stream=True
)

for line in twitter.iter_lines():
    if line:  # filter out keep-alive lines
        router(response=json.loads(line))
