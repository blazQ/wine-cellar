import datetime
import random
from abc import ABC, abstractmethod
from typing import Any, Tuple

import boto3

from config import DefaultConfig

sqs = boto3.resource('sqs', endpoint_url=DefaultConfig.EXTERNAL_ENDPOINT)


'''
    Generic abstract class for a sensor
    Every sensor has a "sense" method, which calls the implemented get readings method and acts accordingly.
    Every sensor has its own error queue and sensor queue that it can talk to. They are set during initialization.
'''
class Sensor(ABC):
    id: str
    room: str
    sensor_queue: sqs.Queue
    error_queue: sqs.Queue
    failure_rate: float

    def __init__(self, sensor_queue:sqs.Queue, error_queue:sqs.Queue, id:str, room:str = "Room 1", failure_rate:float = DefaultConfig.DEFAULT_FAILURE_RATE) -> None:
        super().__init__()
        self.sensor_queue = sensor_queue
        self.error_queue = error_queue
        self.failure_rate = failure_rate
        self.id = id
        self.room = room
    
    @abstractmethod
    def get_readings_sensor(self) -> Tuple[int, float]:
        pass

    def get_readings(self) -> Tuple[int, Any, str]:
        status_code, reading = self.get_readings_sensor()
        return status_code, reading, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def sense(self):
        (code, reading, timestamp) = self.get_readings()
        if code == 1:
            error_msg = '{"device_id": "%s", "device_type": "%s", "room": "%s", "timestamp": "%s"}' % (self.id, type(self).__name__, self.room, timestamp)
            print(error_msg)
            self.error_queue.send_message(MessageBody=error_msg)
        else:
            msg_body = '{"device_id": "%s", "device_type": "%s", "room": "%s", "timestamp": "%s", "reading": "%s"}' \
                        % (self.id, type(self).__name__, self.room, timestamp, reading)
            print(msg_body)
            self.sensor_queue.send_message(MessageBody=msg_body)

        

class TemperatureSensor(Sensor):

    def get_readings_sensor(self) -> Tuple[int, float]:
        status_code = 1
        temperature = 0
        if random.uniform(0,1)>self.failure_rate:
            status_code = 0
            temperature = round(random.uniform(2.0, 20.0), 3) # if above 15 or below 10, there's a problem. Activate cooling and sent notification
        return status_code, temperature


class DewpointSensor(Sensor):

    def get_readings_sensor(self) -> Tuple[int, float]:
        status_code = 1
        dew_point = 0
        if random.uniform(0,1)>self.failure_rate:
            status_code = 0
            dew_point = round(random.uniform(5.0, 9.0), 4) # ideal is 4°C, if above 6 there's a problem, activate ventilation.
        
        return status_code, dew_point
    

class VibrationSensor(Sensor):

    def get_readings_sensor(self) -> Tuple[int, float]:
        status_code = 1
        vibration = 0
        if random.uniform(0,1)>self.failure_rate:
            status_code = 0
            vibration = round(random.uniform(0, 3.0), 3) # ideal is 0 hz, no vibration, if above 1 send urgent telegram notification
        
        return status_code, vibration 
    
class DoorSensor(Sensor):
    
    def get_readings_sensor(self) -> Tuple[int, str]:
        status_code = 1
        door_status = "Closed"
        if random.uniform(0, 1) > self.failure_rate:
            status_code = 0
            door_status_code = random.randint(0,5)
            if door_status_code > 1:
                door_status = "Open"
            else:
                door_status = "Closed" # If it remains open for too long, send email notification to all employees and close it automatically.
        return status_code, door_status



if __name__ == '__main__':
    queue_name = "temperatureQueue"
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    error_queue_name = "errors"
    error_queue = sqs.get_queue_by_name(QueueName=error_queue_name)
    sensor_test = TemperatureSensor(queue, error_queue, "testSensor", "Sweets", 0)
    sensor_test.sense()