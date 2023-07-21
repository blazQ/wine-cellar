import datetime
import json
import uuid
import boto3

from config import DefaultConfig

'''
    Takes a value from the Door Sensor Queue and uploads it to Kinesis
'''

def lambda_handler(event, context):
    s3 = boto3.resource('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    kinesis = boto3.client('kinesis', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    for record in event['Records']:

        # Save record for future inspection
        payload = record["body"]
        timestamp_date = datetime.datetime.now()
        timestamp_str = str(timestamp_date.strftime("%Y-%m-%d %H:%M:%S"))
        id = record["messageId"]
        payload_json = json.loads(payload)
        key = id + '-' + payload_json['device_type'] + '-' + timestamp_str
        s3.Bucket(DefaultConfig.BUCKET_DUMP_DEFAULT_NAME).put_object(
            Key=key, Body=payload
        )

        # Timestamp record and save it to Kinesis
        payload_json['timestamp'] = timestamp_date.timestamp()
        response = kinesis.put_record(
            StreamName=DefaultConfig.KINESIS_DATA_STREAM + payload_json['room'],
            Data=json.dumps(payload_json),
            PartitionKey=str(uuid.uuid4())
        )
        
        return response
