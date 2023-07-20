import base64
import datetime
import json
import logging
import uuid

import boto3
from botocore.exceptions import ClientError

from config import DefaultConfig

'''
    Takes a value from Dynamo and checks if the door has been open for 10 minutes
'''

#TODO: Reimplement Kinesis instead of Dynamo

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    sns = boto3.client('sns', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    # Query the DB for the corresponding room
    response = dynamodb.scan(TableName=DefaultConfig.NOSQL_TABLE_DEFAULT_NAME)

    items = response['Items']

    for item in items:
        door_status = item['door_status']['S']
        door_timestamp = item['door_timestamp']['N']
        if door_status == 'Open' and (datetime.datetime.now().timestamp() - float(door_timestamp) >= DefaultConfig.WAITING_TIME): # 10 minutes
            # send message to SNS
            subject = "Door left open!"
            sns.publish(TopicArn=DefaultConfig.SNS_DEFAULT_TOPIC_ARN, Message=json.dumps({'default': json.dumps(item)}), 
                               MessageStructure='json', Subject=subject) 
            

