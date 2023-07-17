import logging
import json
import datetime
import uuid
import boto3
import base64
from config import DefaultConfig
from botocore.exceptions import ClientError

'''
    Takes a value from the Kinesis Data Stream and checks if the door has been open for 10 minutes
'''

# TODO: Slightly modify the logic in order to connect every x minutes to the stream and get only the latest value

def lambda_handler(event, context):
    s3 = boto3.resource('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    for record in event['Records']:
        payload=base64.b64decode(record["kinesis"]["data"])
        result = json.loads(json.loads(payload))
        # Check the door status
        door_status = result['reading']
        timestamp = result['timestamp']
        if door_status == 'Open':
            # Check the timestamp
            timestamp_unix = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timestamp()
            timestamp_now = datetime.datetime.now().timestamp()
            if timestamp_now - timestamp_unix >= DefaultConfig.WAITING_TIME:
                # Send message on the SNS topic
                s3.Bucket(DefaultConfig.BUCKET_DUMP_DEFAULT_NAME).put_object(
                    Key="magnana", Body=payload
        )
        else: return {
            "ResponseCode" : '200',
            "Message": "Lambda function successfully executed."
        }