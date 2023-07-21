import datetime
import json
import boto3

from config import DefaultConfig

'''
    Takes a value from Kinesis and checks if the door has been open for 10 minutes
'''

def lambda_handler(event, context):
    kinesis = boto3.client('kinesis', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    sns = boto3.client('sns', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

    responses = []
    for room in DefaultConfig.ROOM_CONFIGURATION:
        stream_name = DefaultConfig.KINESIS_DATA_STREAM + room
        # There's only one shard per stream 
        shard_id = 'shardId-000000000000'
        # Iterate over the shard by trimming to the last unprocessed value.
        response = kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='TRIM_HORIZON'
        )

        shard_iterator = response['ShardIterator']

        # Access the latest record available
        response = kinesis.get_records(ShardIterator=shard_iterator)
        records = response['Records']

        if records:
            # Obtain json object of the most recent record and check the status
            last_record = json.loads(get_most_recent_record(records=records)['Data'].decode('utf-8'))
            door_status = last_record['reading']
            # If the door's been open for a certain threshold time, notify.
            if door_status == 'Open' and datetime.datetime.now().timestamp() - float(last_record['timestamp']) >= DefaultConfig.WAITING_TIME:
                response = sns.publish(TopicArn=DefaultConfig.SNS_DEFAULT_TOPIC_ARN, Message=json.dumps({'default': json.dumps(last_record)}), 
                            MessageStructure='json', Subject="Door left open!")
            # Else, do nothing.
            else: responses.append({
                'statusCode': 200,
                'body': "The door is either closed or not been open for enough time.",
                'diff': datetime.datetime.now().timestamp() - float(last_record['timestamp']),
            })
        else:
            responses.append({
                'statusCode': 204,
                'body': "Stream empty!"
            })
    return responses

def get_most_recent_record(records):
    max_record = 0
    for i, record in enumerate(records):
        if record['ApproximateArrivalTimestamp'] > records[max_record]['ApproximateArrivalTimestamp']:
            max_record = i
    return records[max_record]

