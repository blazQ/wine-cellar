import sensors
import boto3
import random
import argparse
import time

from config import DefaultConfig

sqs = boto3.resource('sqs', endpoint_url=DefaultConfig.EXTERNAL_ENDPOINT)


def massive_script_test(queue_names, error_queue, room_names, error_threshold, nmeasurements):
    sensors = []
    for key in queue_names.keys():
        current_sensor_type_list = []
        current_queue = sqs.get_queue_by_name(QueueName=key)
        for i in range(0, nmeasurements):
            random_room = random.randint(0, 4)
            current_sensor_type_list.append(queue_names.get(key)(current_queue, error_queue,
                                                                 f"{queue_names.get(key).__name__}-{i}",
                                                                 room_names[random_room], error_threshold))
        sensors.append(current_sensor_type_list)

    for sensor_type_list in sensors:
        for sensor in sensor_type_list:
            sensor.sense()
            time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="sensorTestScript",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a", "-all", help="massively test all sensors on all default rooms", action='store_true')
    parser.add_argument("-st", "-sensor-type", help="test with a specific sensor type", type=str, default="Temperature")
    parser.add_argument("-r", "-room", help="test on a specific room", type=str, default="Sweets")
    parser.add_argument("-e", "-error", help="set error probability", type=float, default=0.1)
    parser.add_argument("-n", "-nmeasurements", help="set number of repetitions for every sensor type in all mode, or for single in single mode",
                        type=int, default=1)
    args = parser.parse_args()
    config = vars(args)

    queue_names =   {
                        DefaultConfig.DEWPOINT_QUEUE_DEFAULT_NAME: sensors.DewpointSensor,
                        DefaultConfig.DOOR_QUEUE_DEFAULT_NAME: sensors.DoorSensor,
                        DefaultConfig.VIBRATION_QUEUE_DEFAULT_NAME: sensors.VibrationSensor,
                        DefaultConfig.TEMPERATURE_QUEUE_DEFAULT_NAME: sensors.TemperatureSensor
                    }
    error_queue = sqs.get_queue_by_name(QueueName=DefaultConfig.ERROR_QUEUE_DEFAULT_NAME)
    error_threshold = config['e']
    nmeasurements = config['n']
    if config['a'] == True:
        room_names = [
            'Sweets',
            'Full-bodied-reds',
            'Light-to-medium-bodied-reds',
            'Sparklings',
            'Dry-Whites'
        ]
        massive_script_test(queue_names=queue_names, error_queue=error_queue, room_names=room_names,
                             error_threshold=error_threshold, nmeasurements=nmeasurements)
    else:
        sensor_type = config['st']
        room = config['r']
        default_queue_name = None
        # Get the type name
        if sensor_type == 'Temperature':
            default_queue_name = DefaultConfig.TEMPERATURE_QUEUE_DEFAULT_NAME
            sensor_type = queue_names.get(default_queue_name)
        elif sensor_type == 'Vibration':
            default_queue_name = DefaultConfig.VIBRATION_QUEUE_DEFAULT_NAME
            sensor_type = queue_names.get(default_queue_name)
        elif sensor_type == 'Dewpoint':
            default_queue_name = DefaultConfig.DEWPOINT_QUEUE_DEFAULT_NAME
            sensor_type = queue_names.get(default_queue_name)
        else:
            default_queue_name = DefaultConfig.DOOR_QUEUE_DEFAULT_NAME
            sensor_type = queue_names.get(default_queue_name)

        default_queue = sqs.get_queue_by_name(QueueName=default_queue_name)
        # Instantiate based on the type name
        sensor = sensor_type(default_queue, error_queue, f"{queue_names.get(default_queue_name).__name__}",
                             room, error_threshold)
        for i in range(0, nmeasurements):
            sensor.sense()
