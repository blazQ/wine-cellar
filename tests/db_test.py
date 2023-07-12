# Initialize DynamoDB client
import boto3
import time
from datetime import datetime, timedelta

dynamodb = boto3.client('dynamodb', endpoint_url="http://localhost:4566")


now = datetime.now()
now_unix = now.timestamp()
room_name = "Room 1"

# Query the table for items with timestamp greater than or equal to the calculated timestamp
response = dynamodb.query(
    TableName='RoomStatus',
    KeyConditionExpression='#r = :room_name',
    ExpressionAttributeNames={
        '#r': 'room_name'
    },
    ExpressionAttributeValues={
        ':room_name': {'S': room_name}
    }
)

item = response['Items'][0]
print(item.get('current_vibration', False))

dynamodb.update_item(
    TableName='RoomStatus',
    Key={
        'room_name': {'S': item['room_name']['S']},
    },
    ExpressionAttributeNames={
        '#ts': 'timestamp',
    },
    UpdateExpression='SET current_vibrations = :vib, #ts = :ts',
    ExpressionAttributeValues={
        ':vib': {'N': str(1)},
        ':ts': {'N': str(now_unix)}
    }
)


