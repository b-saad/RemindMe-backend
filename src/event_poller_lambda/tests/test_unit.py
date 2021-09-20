import pytest
import os

def test_handler(event_poller):
	print(event_poller.EVENT_TABLE_NAME)
	assert 2 == 1
