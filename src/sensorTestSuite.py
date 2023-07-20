import sensors
import boto3
import random

from config import DefaultConfig

sqs = boto3.resource('sqs', endpoint_url=DefaultConfig.EXTERNAL_ENDPOINT)

if __name__ == '__main__':
    queue_names =   {
                        DefaultConfig.DEWPOINT_QUEUE_DEFAULT_NAME: sensors.DewpointSensor, 
                        DefaultConfig.DOOR_QUEUE_DEFAULT_NAME: sensors.DoorSensor, 
                        DefaultConfig.VIBRATION_QUEUE_DEFAULT_NAME: sensors.VibrationSensor,
                        DefaultConfig.TEMPERATURE_QUEUE_DEFAULT_NAME: sensors.TemperatureSensor
                    }
    error_queue = sqs.get_queue_by_name(QueueName=DefaultConfig.ERROR_QUEUE_DEFAULT_NAME)

    room_names = [
        'Sweets',
        'Full-bodied reds',
        'Light-to-medium bodied reds',
        'Sparklings',
        'Dry Whites'
    ]

    sensors = []
    for key in queue_names.keys():
        current_sensor_type_list = []
        current_queue = sqs.get_queue_by_name(QueueName=key)
        for i in range(0, 9):
            random_room = random.randint(0, 4)
            current_sensor_type_list.append(queue_names.get(key)(current_queue, error_queue, f"{queue_names.get(key).__name__}-{i}", room_names[random_room], 1))
        sensors.append(current_sensor_type_list)
    
    for sensor_type_list in sensors:
        for sensor in sensor_type_list:
            sensor.sense()

    # TODO: Create another kind of test suite to simply test individual sensors instead of all sensors massively