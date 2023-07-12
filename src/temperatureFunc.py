import logging
import json
import datetime
import time
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    s3 = boto3.resource('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    dynamodb = boto3.client('dynamodb', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

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
        # Store value inside db
        temperature = payload_json['reading']
        room_name = payload_json['room']
        timestamp_unix =  timestamp_date.timestamp()# Converting it to UNIX timestamp

        # Querying for current room status
        response = dynamodb.query(
            TableName=DefaultConfig.NOSQL_TABLE_DEFAULT_NAME,
            KeyConditionExpression='#r = :room_name',
            ExpressionAttributeNames={
                '#r': 'room_name'
            },
            ExpressionAttributeValues={
                ':room_name': {'S': room_name}
            }
        )

        if response['Count'] == 1:
            room_status = response['Items'][0]
            dynamodb.update_item(
                TableName='RoomStatus',
                Key={
                    'room_name': {'S': room_status['room_name']['S']},
                },
                ExpressionAttributeNames={
                    '#ts': 'timestamp',
                },
                UpdateExpression='SET current_temperature = :temp, #ts = :ts',
                ExpressionAttributeValues={
                    ':temp': {'N': temperature},
                    ':ts': {'N': str(timestamp_unix)}
                }
            )
            return {
                'statusCode': 200,
                'body': 'Lambda function executed successfully.',
            }
        else:
            return {
               'statusCode': 200, 
               'body': 'Lambda function failed. System might not be initialized.'
            }
