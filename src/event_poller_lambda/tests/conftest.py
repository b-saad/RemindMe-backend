import pytest
from moto import mock_sqs
import os

@pytest.fixture(scope="session")
def event_poller():
	"""
	expose lambda functions
	"""
	env_vars = {
		"EVENT_TABLE_NAME": "TestTable",
		"EVENT_TABLE_SECONDARY_INDEX": "TestSecondaryIndex",
		"LOG_LEVEL": "DEBUG",
		"SMS_QUEUE_NAME": "TestSmsQueue",
		"EMAIL_QUEUE_NAME": "TestEmailQueue",
		"EVENT_WINDOW_START_DELAY": "30",
		"EVENT_WINDOW_LENGTH": "600"
	}
	os.environ.update(env_vars)
	from ..src import event_poller
	yield event_poller


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def sqs_client(aws_credentials):
    with mock_sqs():
        conn = boto3.client("sqs", region_name="us-east-1")
        yield conn
