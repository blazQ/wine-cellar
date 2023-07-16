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
def lambda_handler(event, context):
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
            if timestamp_now - timestamp_unix >= 600:
                # Send message on the SNS topic
                return "DAMN SON!"
        else: return {
            "ResponseCode" : '200',
            "Message": "Lambda function successfully executed."
        }