import boto3
import json
from config import DefaultConfig

dynamoDB = boto3.client('dynamodb', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

def lambda_handler(event, context):
    if 'queryStringParameters' in event and 'room_name' in event['queryStringParameters']:
        room_name = event['queryStringParameters']['room_name']
        response_body = json.dumps(query_dynamo(DefaultConfig.NOSQL_TABLE_DEFAULT_NAME, room_name=room_name))
    else:
        response_body = json.dumps(scan_dynamo(DefaultConfig.NOSQL_TABLE_DEFAULT_NAME))

    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
            'Content-Type': "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': response_body
    }
     

def scan_dynamo(table_name):
    response = dynamoDB.scan(TableName=table_name)
    return response['Items']

def query_dynamo(table_name, room_name):
    query_response = dynamoDB.query(
            TableName=table_name,
            KeyConditionExpression='#r = :room_name',
            ExpressionAttributeNames={
                '#r': 'room_name'
            },
            ExpressionAttributeValues={
                ':room_name': {'S': room_name}
            }
        )
    if query_response['Count'] == 1:
            return query_response['Items'][0]
    else: return ""