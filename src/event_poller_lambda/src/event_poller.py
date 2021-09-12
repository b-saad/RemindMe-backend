import boto3
from botocore.exceptions import ClientError
import json
import logging
import math
import os
import time
from datetime import datetime
from typing import Dict, Optional

EVENT_TABLE_NAME = os.environ.get("EVENT_TABLE_NAME")
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
SMS_QUEUE_NAME = os.environ.get("SMS_QUEUE_NAME")
EMAIL_QUEUE_NAME = os.environ.get("EMAIL_QUEUE_NAME")

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

def handler(event, context):
	pass
