import logging
import json
import datetime
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError

''' 
    Invoked whenever a vapor pressure value is ready on the vapor pressure queue.
    It retrieves the current temperature from the DB for the associated room, then proceeds in calculating the relative humidity.
    The resulting value is stored inside the DB.
'''

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    for record in event['Records']:
        payload = record["body"]
        payload_json = json.loads(payload)
        vapor_pressure = float(payload_json['vapor_pressure'])
        room_name = payload_json['room']
        timestamp_unix =  datetime.datetime.now().timestamp()

        # Querying for current room status
        query_response = dynamodb.query(
            TableName=DefaultConfig.NOSQL_TABLE_DEFAULT_NAME,
            KeyConditionExpression='#r = :room_name',
            ExpressionAttributeNames={
                '#r': 'room_name'
            },
            ExpressionAttributeValues={
                ':room_name': {'S': room_name}
            }
        )

        if query_response['Count'] == 1:
            room_status = query_response['Items'][0]
            current_temperature = room_status['current_temperature']['N']
            saturated_vapor_pressure = compute_saturated_vapor_pressure(float(current_temperature))
            humidity = round((vapor_pressure/saturated_vapor_pressure) * 100, 2)
            # Adjusting humidity   
            update_response = dynamodb.update_item(
                TableName='RoomStatus',
                Key={
                    'room_name': {'S': room_status['room_name']['S']},
                },
                ExpressionAttributeNames={
                    '#ts': 'timestamp',
                },
                UpdateExpression='SET current_humidity = :hum, #ts = :ts',
                ExpressionAttributeValues={
                    ':hum': {'N': str(humidity)},
                    ':ts': {'N': str(timestamp_unix)}
                }
            )
            return update_response
        else: return query_response

def compute_saturated_vapor_pressure(current_temperature:float) -> float:
    return 6.11 * 10.0 * ((7.5 * current_temperature)/(237.3 + current_temperature))
