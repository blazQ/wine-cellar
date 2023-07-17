import logging
import json
import datetime
import time
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError


# TODO: Implement logic to structure che notification based on the content and send it to the bot

def lambda_handler(event, context):
    s3 = boto3.resource('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    for record in event['Records']:
        payload = record["Sns"]
        # TEST
        s3.Bucket(DefaultConfig.BUCKET_DUMP_DEFAULT_NAME).put_object(
            Key=record['Sns']['MessageId'], Body=str(payload)
        )
        # TAKE RELEVANT DATA

        # SEND PAYLOAD TO TELEGRAM BOT
        return payload