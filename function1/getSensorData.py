import boto3
import json
from config import DefaultConfig

s3 = boto3.client('s3', endpoint_url=DefaultConfig.INTERNAL_ENDPOINT)

def lambda_handler(event, context):
    if 'queryStringParameters' in event and 'sensor_type' in event['queryStringParameters']:  # Get all measurements based on a sensor type
        return_body = []
        measurements = []
        response = s3.list_objects(
            Bucket=DefaultConfig.BUCKET_DUMP_DEFAULT_NAME,
        )
        # filtering only sensor specific measurements
        if 'Contents' in response:
            object_keys = [item['Key'] for item in response['Contents'] if event['queryStringParameters']['sensor_type'] in item['Key']]
            # retrieving the content of the objects
            for key in object_keys:
                response_object = s3.get_object(Bucket=DefaultConfig.BUCKET_DUMP_DEFAULT_NAME, Key=key)
                measurement = response_object['Body'].read().decode('utf-8')
                measurements.append(json.loads(measurement))
            # if measurements for a specific room were asked:
            if 'room_name' in event['queryStringParameters']:
                # consider only the relevant measurements when making the charts
                relevant_measurements = [(item['reading'], item['timestamp'], item['room']) for item in measurements if item['room'] == event['queryStringParameters']['room_name']]
                return_body = relevant_measurements
            else: # if not, create charts for all rooms present
                for room in DefaultConfig.ROOM_CONFIGURATION:
                    room_measurements = [(item['room']) for item in measurements if item['room'] == room]
                    # if there are measurements
                    if room_measurements:
                        # add them to return body
                        return_body.append(room_measurements)

        else: return_body = "No data!"

    else: # Return error
        return_body = "No data!"

    return {
        'isBase64Encoded': True,
        'statusCode': 200,
        'headers': {
            'Content-Type': "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': return_body
    }

