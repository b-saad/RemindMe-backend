import boto3
from botocore.exceptions import ClientError
import json
import logging
import math
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from twilio.rest import Client

EVENT_KEY_TIMESTAMP = "EventTimestamp"
EVENT_KEY_TARGET = "Target"
EVENT_KEY_MESSAGE = "Message"

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()



# Your Account SID from twilio.com/console
TWILLIO_ACCOUNT_SID = os.environ.get("TWILLIO_ACCOUNT_SID")
# Your Auth Token from twilio.com/console
TWILLIO_AUTH_TOKEN = os.environ.get("TWILLIO_AUTH_TOKEN")
TWILLIO_PHONE_NUMBER = os.environ.get("TWILLIO_PHONE_NUMBER")

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

twillio_client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)

def _send_sms(phone_number: str, message: str):
	"""
	"""
	twillio_client.calls.create(
		to=phone_number,
		from_=TWILLIO_PHONE_NUMBER,
		body=message
	)

def handler(event, context):
	pass
