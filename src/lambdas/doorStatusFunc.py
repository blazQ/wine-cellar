import logging
import json
import uuid
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError

'''
    Takes a value from the Door Sensor Queue and uploads it to a Kinesis Data Stream 
'''

def lambda_handler(event, context):
    kinesis = boto3.client('kinesis', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    for record in event['Records']:
        # Get the payload
        payload = record["body"]
        # Get it on kinesis
        response = kinesis.put_record(
            StreamName=DefaultConfig.KINESIS_DATA_STREAM,
            Data=json.dumps(payload),
            PartitionKey=str(uuid.uuid4())
        )
        return response