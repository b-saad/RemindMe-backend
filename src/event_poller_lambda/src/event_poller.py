import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import json
import logging
import math
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

EVENT_TYPE_EMAIL = "email"
EVENT_TYPE_SMS = "sms"

EVENT_KEY_TIMESTAMP = "EventTimestamp"
EVENT_KEY_WINDOW_START = "EventWindowStart"
EVENT_KEY_EVENT_TYPE = "EventType"

EVENT_TABLE_NAME = os.environ.get("EVENT_TABLE_NAME")
EVENT_TABLE_SECONDARY_INDEX = os.environ.get("EVENT_TABLE_SECONDARY_INDEX")
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
SMS_QUEUE_NAME = os.environ.get("SMS_QUEUE_NAME")
EMAIL_QUEUE_NAME = os.environ.get("EMAIL_QUEUE_NAME")
EVENT_WINDOW_START_DELAY = os.environ.get("EVENT_WINDOW_START_DELAY", "300")
EVENT_WINDOW_LENGTH = os.environ.get("EVENT_WINDOW_LENGTH")

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)


def _get_previous_ten_minute_interval_start(timestamp: int) -> int:
    """
    Gets the start of 10 minute interval for the current timestamp
    
    Returns:
        Unix timestamp for start of last 10 min interval
    """
    event_timestamp = datetime.utcfromtimestamp(timestamp) 
    interval_start = event_timestamp - timedelta(minutes=event_timestamp.minute % 10,
                                                seconds=event_timestamp.second,
                                                microseconds=event_timestamp.microsecond)
    return int(interval_start.timestamp())

def _get_next_window_bounds() -> (int, int):
    """
    Gets the lower and upper bounds of the next window in unix time stamps

    Returns:
        (Unix Timestamp, Unix Timestamp)
    """
    in_next_window = datetime.utcnow() + timedelta(seconds=int(EVENT_WINDOW_START_DELAY))
    lower_bound = _get_previous_ten_minute_interval_start(int(in_next_window.timestamp()))
    upper_bound = lower_bound + int(EVENT_WINDOW_LENGTH)
    return (lower_bound, upper_bound)


def _get_events_from_next_window() -> List[Dict]:
    """
    Fetches events from persistent store

    Returns:
        List of events in next window
    """
    window_lower_bound, window_upper_bound = _get_next_window_bounds()
    table = boto3.resource('dynamodb').Table(EVENT_TABLE_NAME)
    response = table.query(  
        IndexName=EVENT_TABLE_SECONDARY_INDEX,
        KeyConditionExpression=Key(EVENT_KEY_WINDOW_START).eq(window_lower_bound) & 
                               Key(EVENT_KEY_TIMESTAMP).between(window_lower_bound, window_upper_bound)
    )
    logger.info("Retrieved %d events from DB", len(response["Items"]))
    return response["Items"]


def _time_delta_from_now(timestamp: str) -> bool:
    """
    Returns the time difference in seconds between now and the timestamp
    
    Args:
        timestamp: The timestamp in unix time
    """
    current_timestamp = datetime.utcnow()
    event_timestamp = datetime.fromtimestamp(int(timestamp))
    time_delta = event_timestamp - current_timestamp
    time_delta_seconds = math.ceil(time_delta.total_seconds())
    return time_delta_seconds


def _schedule_event(event: Dict, queue):
    """
    Schedule event to be processed through stream

    Args:
        request: event received by lambda
    """
    for k, v in event.items():
        if isinstance(v, Decimal):
            event[k] = int(v)
    delay = _time_delta_from_now(event[EVENT_KEY_TIMESTAMP]) - 5
    delay = max(0, delay)
    try:
        response = queue.send_message(
            MessageBody=json.dumps(event),
            DelaySeconds=delay
        )
        if 'Failed' in response:
            logger.error("Failed to add event %s to SQS queue. Response: %s", event, response)
    except ClientError as e:
        logger.error("Failed to add event %s to SQS queue. Error: %s", event, e)


def _schedule_events(events: List[Dict]):
    """
    Schedules events with appropriate delays in SQS queues
    """
    sqs = boto3.resource('sqs')
    sms_queue = sqs.get_queue_by_name(QueueName=SMS_QUEUE_NAME)
    email_queue = sqs.get_queue_by_name(QueueName=EMAIL_QUEUE_NAME) 
    for event in events:
        logger.debug("Scheduling event %s", event)
        if event[EVENT_KEY_EVENT_TYPE] == EVENT_TYPE_EMAIL:
            _schedule_event(event, email_queue)
        elif event[EVENT_KEY_EVENT_TYPE] == EVENT_TYPE_SMS:
            _schedule_event(event, sms_queue)


def handler(event, context):
    """
    Retrieve events for the near future from data store and schedule them
    """
    events = _get_events_from_next_window()	
    _schedule_events(events)

