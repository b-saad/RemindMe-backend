import boto3
from botocore.exceptions import ClientError
import json
import logging
import math
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from twilio.rest import Client

EVENT_KEY_TIMESTAMP = "EventTimestamp"
EVENT_KEY_TARGET = "Target"
EVENT_KEY_MESSAGE = "Message"

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()



# Your Account SID from twilio.com/console
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
# Your Auth Token from twilio.com/console
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def _send_sms(phone_number: str, message: str):
	"""
	"""
	twilio_client.messages.create(
		to=phone_number,
		from_=TWILIO_PHONE_NUMBER,
		body=message
	)


def handler(event, _):
	logger.debug("Received event %s", event)
	events = [json.loads(record.get("body", "{}")) for record in event["Records"]]
	logger.info('Processing %d records', len(events))

	# sort the events by timestamp
	events = sorted(events, key=lambda k: int(k[EVENT_KEY_TIMESTAMP])) 

	for sms_event in events:
		scheduled_time = datetime.utcfromtimestamp(sms_event[EVENT_KEY_TIMESTAMP])

		delay = (scheduled_time - datetime.utcnow()).total_seconds()

		# remove another 10ms as there will be a short delay
		delay -= 0.01
		if delay > 0:
			time.sleep(delay)

		try:
			_send_sms(sms_event[EVENT_KEY_TARGET], sms_event[EVENT_KEY_MESSAGE])
			now = datetime.utcnow()
			logger.info("Processed event: %s at %s", sms_event, now)
		except Exception as e:
			logger.error("Failed to process event %s. Error: %s", sms_event, e)

