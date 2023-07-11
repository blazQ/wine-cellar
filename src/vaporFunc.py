import logging
import json
import datetime
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    sqs = boto3.resource('sqs', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    s3 = boto3.resource('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    for record in event['Records']:
        # Save record for future inspection
        payload = record["body"]
        timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        id = record["messageId"]
        payload_json = json.loads(payload)
        key = id + '-' + payload_json['device_type'] + '-' + timestamp
        s3.Bucket(DefaultConfig.BUCKET_DUMP_DEFAULT_NAME).put_object(
            Key=key, Body=payload
        )
        # Compute vapor pressure
        dew_point = float(payload_json['reading'])
        vapor_pressure = compute_vapor_pressure(dew_point)
        # Load it into the second queue
        vapor_pressure_queue = sqs.get_queue_by_name(QueueName=DefaultConfig.VAPOR_PRESSURE_QUEUE_DEFAULT_NAME)
        # JSON is better
        vapor_pressure_dict = {'vapor_pressure': vapor_pressure, 
                               'timestamp': timestamp
                               }
        message = json.dumps(vapor_pressure_dict)
        vapor_pressure_queue.send_message(MessageBody=message)

        return vapor_pressure

def compute_vapor_pressure(dew_point:float):
    return 6.11 * 10.0 * ((7.5 * dew_point)/(237.3 + dew_point))

