import logging
import json
import datetime
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError

'''
    Gets executed every 10 minutes and check wheter the storage conditions are met
    Loads storage conditions for each room from a json file
    Loads rooms
    Checks if each room is within the accepted ranges
    If not, sends notifications.
'''
def lambda_handler(event, context):
    f = open('storage_conditions.json')
    storage_conditions = json.load(f)
    dynamodb = boto3.client('dynamodb', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    sns = boto3.client('sns', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    for room in storage_conditions['rooms']:
        room_name = room['room_name']
        # Query the DB for the corresponding room
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
            # Get the status
            room_status = query_response['Items'][0]
            # Verify that values are within range
            current_temperature = float(room_status['current_temperature']['N'])
            current_humidity = float(room_status['current_humidity']['N'])
            current_vibration = float(room_status['current_vibration']['N'])
            h_check = humidity_check(current_humidity, room)
            t_check = temperature_check(current_temperature, room)
            v_check = vibration_check(current_vibration, room)
            # If one of the checks didn't go through
            if not h_check or not t_check or not v_check:
                payload = {'room_name': room_name, 'humidity_check': h_check, 'temperature_check': t_check, 'vibration_check': v_check, 'timestamp': datetime.datetime.now().timestamp()}
                subject = "Routine Check Errors"
                # Sends notification to the topic
                sns.publish(TopicArn=DefaultConfig.SNS_DEFAULT_TOPIC_ARN, Message=json.dumps({'default': json.dumps(payload)}), 
                               MessageStructure='json', Subject=subject)
        else: return query_response


def humidity_check(current_humidity, room):
    min_humidity = room['min_humidity']
    max_humidity = room['max_humidity']
    return min_humidity <= current_humidity <= max_humidity

def temperature_check(current_temperature, room):
    max_temperature = room['max_temperature']
    min_temperature = room['min_temperature']
    return min_temperature <= current_temperature <= max_temperature

def vibration_check(current_vibration, room):
    max_vibration = room['max_vibrations']
    return current_vibration <= max_vibration

