import logging
import json
import datetime
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    sqs = boto3.resource('sqs', endpoint_url='http://host.docker.internal:4566')
    s3 = boto3.resource('s3', endpoint_url='http://host.docker.internal:4566')

    for record in event['Records']:
        # Save record for future inspection
        payload = record["body"]
        id = record["messageId"]
        s3.Bucket("mybucket").put_object(
            Key=id, Body=payload
        )
        # Compute vapor pressure
        payload_json = json.loads(payload)
        dew_point = float(payload_json['reading'])
        vapor_pressure = compute_vapor_pressure(dew_point)
        # Load it into the second queue
        vapor_pressure_queue = sqs.get_queue_by_name(QueueName="vaporPressureQueue")
        # JSON is better
        vapor_pressure_dict = {'vapor_pressure': vapor_pressure, 
                               'timestamp': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                               }
        message = json.dumps(vapor_pressure_dict)
        vapor_pressure_queue.send_message(MessageBody=message)

        return vapor_pressure

def compute_vapor_pressure(dew_point:float):
    return 6.11 * 10.0 * ((7.5 * dew_point)/(237.3 + dew_point))

