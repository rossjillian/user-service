import json
import boto3
from botocore.config import Config
import getcredentials as gc

my_config = Config(
    region_name='us-east-1'
)

vars = gc.get_cred()
keyid = vars[0]
pw = vars[1]

client = boto3.client('sns', aws_access_key_id=keyid,
                      aws_secret_access_key=pw,
                      config=my_config)

filters = {
    '/registration': {
        'methods': ['POST'],
        'topic': None   # AWS SNS Topic
    }
}


def publish_string(topic, json_data):
    s = json.dumps(json_data, default=str)
    res = client.publish(TopicArn=topic, Message=s)
    return res


def notify(request, response):
    type = response.status.split(' ')[1]
    path = request.path
    method = request.method
    body = request.json

    filter = filters.get(path, None)

    if filter is not None:
        if method in filter['methods']:
            event = {
                'resource': path,
                'method': method,
                'data': body,
                'type': type
            }
            topic = filter['topic']

            publish_string(topic, event)

