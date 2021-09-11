import boto3
from botocore.exceptions import ClientError
import json
import logging
import math
import os
import time
from datetime import datetime
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


def _event_in_current_scheduling_window(timestamp: str) -> bool:
    """
    Checks if the provided timestamp is in the current scheduling window
    
    Args:
        timestamp: The event's timestamp in unix time
    """
    current_timestamp = datetime.utcnow()
    event_timestamp = datetime.fromtimestamp(int(timestamp))
    time_delta = event_timestamp - current_timestamp
    time_delta_seconds = math.ceil(time_delta.total_seconds())
    return time_delta_seconds > 5 and time_delta_seconds < int(STORAGE_TIME_DELTA_MINIMUM_SECONDS)


def _create_event_record_from_request(request: Dict) -> Dict:
    """
    Creates normalized event record  

    Args:
        request: valid event received by lambda
    """
    target = request[REQUEST_EMAIL_KEY] if request[REQUEST_EVENT_TYPE_KEY] == EVENT_TYPE_EMAIL else request[REQUEST_PHONE_KEY]
    ttl = int(request[REQUEST_TIMESTAMP_KEY]) + 10 * 60 # 10 mins after scheduled event
    reminder_record = {
        "EventId": str(uuid.uuid4()),
        "EventTimestamp": int(request[REQUEST_TIMESTAMP_KEY]),
        "EventType": request[REQUEST_EVENT_TYPE_KEY],
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
    for _ in range(5):
        try:
            table.put_item(record)
            return
        except ClientError as e:
            logger.error("Failed to add request %s to db. Error: %s", request, e)
            time.sleep(.200)
    logger.error("Failed to save event to db: %s. Will not retry", request)


def _schedule_event(request: Dict):
    """
    Schedule event to be processed through stream

    Args:
        request: event received by lambda
    """
    


def handler(event, context):
    err = _validate_request_body(event)
    if err is not None:
        return _create_json_response(400, err)
    
    if _event_in_current_scheduling_window(event[REQUEST_TIMESTAMP_KEY]):
        _schedule_event(event)
    else:
        _add_event_to_db(event)

    return _create_json_response(200, "Reminder successfully scheduled")
