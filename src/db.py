import boto3
from config import DefaultConfig

dynamodb = boto3.resource('dynamodb', endpoint_url=DefaultConfig.EXTERNAL_ENDPOINT)

table = dynamodb.create_table(
    TableName=DefaultConfig.NOSQL_TABLE_DEFAULT_NAME,
    KeySchema=[
        {
            'AttributeName': 'room_name',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'room_name',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

# TODO
'''Add few instructions to have initial setup '''