import boto3
import datetime
from config import DefaultConfig
from decimal import Decimal

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
now_stamp = Decimal(datetime.datetime.now().timestamp())
                    
table.put_item(Item={'room_name': 'Full-bodied reds', 'door_status': 'Closed', 'door_timestamp': now_stamp, 'current_temperature': 17, 'current_vibration': 0, 'current_humidity': 65, 'timestamp': now_stamp})
table.put_item(Item={'room_name': 'Light-to-medium bodied reds', 'door_status': 'Closed', 'door_timestamp': now_stamp,  'current_temperature': 12, 'current_vibration': 0, 'current_humidity': 80, 'timestamp': now_stamp})
table.put_item(Item={'room_name': 'Dry Whites', 'door_status': 'Closed', 'door_timestamp': now_stamp,  'current_temperature': 10, 'current_vibration': 0, 'current_humidity': 50, 'timestamp': now_stamp})
table.put_item(Item={'room_name': 'Sparklings', 'door_status': 'Closed', 'door_timestamp': now_stamp, 'current_temperature': 6, 'current_vibration': 0, 'current_humidity': 70, 'timestamp': now_stamp})
table.put_item(Item={'room_name': 'Sweets', 'door_status': 'Closed', 'door_timestamp': now_stamp, 'current_temperature': 4, 'current_vibration': 0, 'current_humidity': 65, 'timestamp': now_stamp})