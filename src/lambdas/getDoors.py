import boto3
import json
from config import DefaultConfig

def lambda_handler(event, context):
    kinesis = boto3.client('kinesis', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)
    response_body = []
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
            # Send the status
            response_body.append(last_record)
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
            'Content-Type': "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(json.dumps(response_body))
    }

def get_most_recent_record(records):
    max_record = 0
    for i, record in enumerate(records):
        if record['ApproximateArrivalTimestamp'] > records[max_record]['ApproximateArrivalTimestamp']:
            max_record = i
    return records[max_record]
