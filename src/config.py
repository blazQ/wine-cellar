import os

class DefaultConfig:
    EXTERNAL_ENDPOINT = os.environ.get("ExternalEndpoint", "http://localhost:4566")
    INTERNAL_ENDPOINT = os.environ.get("InternalEndpoint", "http://host.docker.internal:4566")
    NOSQL_TABLE_DEFAULT_NAME = os.environ.get("TableName", "RoomStatus")
    ERROR_QUEUE_DEFAULT_NAME = os.environ.get("ErrorQueueDefName", "errors")
    DEWPOINT_QUEUE_DEFAULT_NAME = os.environ.get("DewPointQueueDefName", "dewPointQueue")
    DOOR_QUEUE_DEFAULT_NAME = os.environ.get("DoorQueueDefName", "doorQueue")
    VIBRATION_QUEUE_DEFAULT_NAME = os.environ.get("VibQueueDefName", "vibrationsQueue")
    VAPOR_PRESSURE_QUEUE_DEFAULT_NAME = os.environ.get("VaporPressQueue", "vaporPressureQueue")
    BUCKET_DUMP_DEFAULT_NAME = os.environ.get("S3DefaultName", "sensorbucket")
    DEFAULT_FAILURE_RATE = os.environ.get("DefaultFailure", 0.5)
    BOT_TOKEN = os.environ.get("BotToken", "")
    BOT_ID = os.environ.get("BotId", "")
    ROOM_CONFIGURATION = os.environ.get("BotId")