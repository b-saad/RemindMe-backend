import boto3
from botocore.exceptions import ClientError
import json
import logging
import math
import os
import time
from datetime import datetime, timedelta
import uuid
from typing import Dict, Optional

EVENT_TYPE_EMAIL = "email"
EVENT_TYPE_SMS = "sms"

REQUEST_TIMESTAMP_KEY = "event_timestamp"
REQUEST_EVENT_TYPE_KEY = "event_type"
REQUEST_MESSAGE_KEY = "message"
REQUEST_EMAIL_KEY = "email"
REQUEST_PHONE_KEY = "phone_number"

EVENT_TABLE_NAME = os.environ.get("EVENT_TABLE_NAME")
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
SMS_QUEUE_NAME = os.environ.get("SMS_QUEUE_NAME")
EMAIL_QUEUE_NAME = os.environ.get("EMAIL_QUEUE_NAME")
STORAGE_TIME_DELTA_MINIMUM_SECONDS = os.environ.get("SCHEDULER_LAMBDA_RATE_SECONDS", "600")

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

def _validate_required_fields(request: Dict) -> Optional[str]:
    """
    Validates request body for expected fields

    Args:
        request: Request/event received by lambda
    
    Returns:
        Optional error message
    """
    required_fields = [REQUEST_TIMESTAMP_KEY, REQUEST_EVENT_TYPE_KEY, REQUEST_MESSAGE_KEY]
    for field in required_fields:
        if field not in request:
            return f"Missing required {field} field in request"
    return None


def _validate_required_fields_content(request: Dict) -> Optional[str]:
    """
    Validates request body for expected formats

    Args:
        request: Request/event received by lambda
    
    Returns:
        Optional error message
    """
    try:
        timestamp = datetime.fromtimestamp(int(request[REQUEST_TIMESTAMP_KEY]))
        if timestamp < datetime.utcnow():
            raise ValueError
    except ValueError:
        return f"{REQUEST_TIMESTAMP_KEY} must be a valid future unix timestamp"
    if request[REQUEST_EVENT_TYPE_KEY] == EVENT_TYPE_EMAIL and REQUEST_EMAIL_KEY not in request:
       return "Missing required email field in request" 
    if request[REQUEST_EVENT_TYPE_KEY] == EVENT_TYPE_SMS and REQUEST_PHONE_KEY not in request:
       return "Missing required phone_number field in request" 
    return None



def _validate_request_body(request: Dict) -> Optional[str]:
    """
    Validates request body for expected fields and formats

    Args:
        request: Request/event received by lambda
    
    Returns:
        Optional error message
    """
    err = _validate_required_fields(request)
    if err:
        return err
    err = _validate_required_fields_content(request)
    if err:
        return err
    return None


def _create_json_response(status_code: int, message: str) -> Dict:
    """
    Creates json response to be returned by the lambda

    Args:
        status_code: HTTP Status code
        message: response message
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": message})
    }


def _time_delta_from_now(timestamp: str) -> bool:
    """
    Returns the time difference in seconds between now and the timestamp
    
    Args:
        timestamp: The timestamp in unix time
    """
    current_timestamp = datetime.utcnow()
    event_timestamp = datetime.utcfromtimestamp(int(timestamp))
    time_delta = event_timestamp - current_timestamp
    time_delta_seconds = math.ceil(time_delta.total_seconds())
    return time_delta_seconds


def _event_in_current_scheduling_window(timestamp: str) -> bool:
    """
    Checks if the provided timestamp is in the current scheduling window
    
    Args:
        timestamp: The event's timestamp in unix time
    """
    time_delta_seconds = _time_delta_from_now(timestamp)
    # we mark time stamps < 0 as valid in window
    return time_delta_seconds < int(STORAGE_TIME_DELTA_MINIMUM_SECONDS)


def _get_previous_ten_minute_interval_start(timestamp: str) -> int:
    """
    Gets the start of 10 minute interval for the current timestamp
    
    Returns:
        Unix timestamp for start of last 10 min interval
    """
    event_timestamp = datetime.utcfromtimestamp(int(timestamp)) 
    interval_start = event_timestamp - timedelta(minutes=event_timestamp.minute % 10,
                                                seconds=event_timestamp.second,
                                                microseconds=event_timestamp.microsecond)
    return int(interval_start.timestamp())


def _create_event_record_from_request(request: Dict) -> Dict:
    """
    Creates normalized event record  

    Args:
        request: valid event received by lambda
    """
    target = request[REQUEST_EMAIL_KEY] if request[REQUEST_EVENT_TYPE_KEY] == EVENT_TYPE_EMAIL else request[REQUEST_PHONE_KEY]
    ttl = int(request[REQUEST_TIMESTAMP_KEY]) + 10 * 60 # 10 mins after scheduled event
    ten_minute_window = _get_previous_ten_minute_interval_start(request[REQUEST_TIMESTAMP_KEY])
    reminder_record = {
        "EventId": str(uuid.uuid4()),
        "EventTimestamp": int(request[REQUEST_TIMESTAMP_KEY]),
        "EventType": request[REQUEST_EVENT_TYPE_KEY],
        "EventWindowStart": ten_minute_window,
        "TimeToLive": ttl,
        "Target": target,
        "Message": request[REQUEST_MESSAGE_KEY]
    }
    return reminder_record


def _add_event_to_db(request: Dict):
    """
    Adds event to DB

    Args:
        request: event received by lambda
    """
    table = boto3.resource('dynamodb').Table(EVENT_TABLE_NAME)
    record = _create_event_record_from_request(request)
    retry_limit = 5
    for attempt in range(retry_limit):
        try:
            table.put_item(Item=record)
            return
        except ClientError as e:
            logger.error("Failed to save event %s to db. Error: %s", request, e)
            if attempt == retry_limit - 1:
                raise
            else:
                time.sleep(.200)


def _schedule_event(request: Dict):
    """
    Schedule event to be processed through stream

    Args:
        request: event received by lambda
    """
    delay = _time_delta_from_now(request[REQUEST_TIMESTAMP_KEY]) - 5
    delay = max(0, delay)
    event = _create_event_record_from_request(request)
    sqs = boto3.resource('sqs')
    queue_name = EMAIL_QUEUE_NAME if request[REQUEST_EVENT_TYPE_KEY] == EVENT_TYPE_EMAIL else SMS_QUEUE_NAME
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    try:
        response = queue.send_message(
            MessageBody=json.dumps(event),
            DelaySeconds=delay
        )
        if 'Failed' in response:
            logger.error("Failed to add event %s to SQS queue. Error: %s", request, response["Failed"])
            raise ClientError(response["Failed"])
    except ClientError as e:
        logger.error("Failed to add event %s to SQS queue. Error: %s", request, e)
        raise


def handler(event, context):
    logger.debug("Received event; %s", event)
    event = json.loads(event['body'])
    err = _validate_request_body(event)
    if err is not None:
        logger.info("Event validation failed. Event: %s, err: %s", event, err)
        return _create_json_response(400, err)
    
    try:
        if _event_in_current_scheduling_window(event[REQUEST_TIMESTAMP_KEY]):
            _schedule_event(event)
        else:
            _add_event_to_db(event)
    except ClientError as e:
        logger.error("Failed to handle event. AWS error. Error: %s", e)
        return _create_json_response(500, "Reminder failed to be scheduled") 

    return _create_json_response(200, "Reminder successfully scheduled")
