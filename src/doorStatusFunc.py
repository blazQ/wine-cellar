import logging
import json
import datetime
import boto3
from config import DefaultConfig
from botocore.exceptions import ClientError

'''Takes value from the door queue. Stores the door status and timestamp on the database'''
'''Gets executed again after 10 minutes with cloudwatch. Retrieves the door status and timestamp from DB.
If the door was open, and the status didn't change in the last 10 minutes, sends a notification
It's better if two functions do this ndr.'''

def lambda_handler(event, context):
    pass
