import json
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

STORAGE_TIME_DELTA_MINIMUM_SECONDS = os.environ.get("SCHEDULER_LAMBDA_RATE_SECONDS")

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


def _is_event_in_current_scheduling_window(timestamp: str) -> bool:
    """
    Checks if the provided timestamp is in the current scheduling window
    
    Args:
        timestamp: The event's timestamp in unix time
    """
    current_timestamp = datetime.utcnow()
    event_timestamp = datetime.fromtimestamp(int(timestamp))
    time_delta = event_timestamp - current_timestamp
    time_delta_seconds = math.ceil(time_delta.total_seconds())
    return time_delta_seconds > STORAGE_TIME_DELTA_MINIMUM_SECONDS


def handler(event, context):
    err = _validate_request_body(event)
    if err is not None:
        return _create_json_response(400, err)

	return _create_json_response(200, "Reminder successfully scheduled")
