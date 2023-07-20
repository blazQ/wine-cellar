import json

import boto3

from config import DefaultConfig


def lambda_handler(event, context):
    sns = boto3.client('sns', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    for record in event['Records']:
        payload = record["body"]
        subject = "Sensor Error"
        response = sns.publish(TopicArn=DefaultConfig.SNS_DEFAULT_TOPIC_ARN, Message=json.dumps({'default': json.dumps(payload)}), 
                               MessageStructure='json', Subject=subject)
        return response
