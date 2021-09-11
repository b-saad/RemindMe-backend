import pytest
import os
from datetime import datetime
from pytest_mock import mocker
import time
from typing import Dict
from ..src import remind_me_api

@pytest.mark.parametrize("event", [
    {},
    {"event_timestamp": "", "message": ""},
    {"event_type": "", "message": ""},
    {"event_timestamp": "", "event_type": ""},
])
def test_validate_required_fields_error(event: Dict):

    # test
    err = remind_me_api._validate_required_fields(event)

    # check
    assert(err != None)


def test_validate_required_fields():
    event = {"event_timestamp": "", "event_type": "", "message": ""}

    # test
    err = remind_me_api._validate_required_fields(event)

    # check
    assert not err


def test_validate_required_fields_content_timestamp_error():
    event =  {"event_timestamp": "1630887677", "event_type": "email","message": "test"}
    # test
    err = remind_me_api._validate_required_fields_content(event)

    # check
    assert(err != None)


@pytest.mark.parametrize("event", [
    {"event_timestamp": "", "event_type": "email", "message": ""},
    {"event_timestamp": "", "event_type": "sms", "message": ""},
    {"event_timestamp": "", "event_type": "sms", "email": "", "message": ""},
    {"event_timestamp": "", "event_type": "email", "phone_number": "", "message": ""},
])
def test_validate_required_fields_content_event_type_error(event: Dict):
    event["event_timestamp"] = str(int(datetime.utcnow().timestamp() + 25))

    # test
    err = remind_me_api._validate_required_fields_content(event)

    # check
    
    assert(err != None)


@pytest.mark.parametrize("event", [
    {"event_timestamp": "", "event_type": "email", "email": "", "message": ""},
    {"event_timestamp": "", "event_type": "sms", "phone_number": "", "message": ""},
])
def test_validate_required_fields_content(event: Dict):
    event["event_timestamp"] = str(int(datetime.utcnow().timestamp() + 25))

    # test
    err = remind_me_api._validate_required_fields_content(event)

    # check
    assert not err


def test_is_event_in_current_scheduling_window_valid(mocker):
    mocker.patch.object(remind_me_api, "STORAGE_TIME_DELTA_MINIMUM_SECONDS", str(10 * 60))
    valid_timestamp = str(int(time.time()) + 100) 
    result = remind_me_api._event_in_current_scheduling_window(valid_timestamp)

    assert result 


def test_is_event_in_current_scheduling_window_right_bound(mocker):
    mocker.patch.object(remind_me_api, "STORAGE_TIME_DELTA_MINIMUM_SECONDS", str(10 * 60))
    invalid_timestamp = str(int(time.time()) + 10*61) 
    result = remind_me_api._event_in_current_scheduling_window(invalid_timestamp)

    assert not result 


def test_is_event_in_current_scheduling_window_left_bound(mocker):
    mocker.patch.object(remind_me_api, "STORAGE_TIME_DELTA_MINIMUM_SECONDS", str(10 * 60))
    invalid_timestamp = 0
    result = remind_me_api._event_in_current_scheduling_window(invalid_timestamp)

    assert not result 


@pytest.mark.parametrize("event", [
    {"event_timestamp": "", "event_type": "email", "email": "test@email.com", "message": "test email msg"},
    {"event_timestamp": "", "event_type": "sms", "phone_number": "", "message": "test sms msg"},
])
def test_create_event_record_from_request(event: Dict):
    # setup
    cur_timestamp = int(datetime.utcnow().timestamp())
    event["event_timestamp"] = str(cur_timestamp)
    expected_target = event["email"] if event["event_type"] == "email" else event["phone_number"]

    # test 
    record = remind_me_api._create_event_record_from_request(event)

    # check
    assert "EventId" in record
    assert isinstance(record["EventId"], str)
    assert "EventTimestamp" in record
    assert record["EventTimestamp"] == cur_timestamp
    assert "TimeToLive" in record
    assert isinstance(record["TimeToLive"], int)
    assert "Message" in record
    assert record["Message"] == event["message"]
    assert "Target" in record
    assert record["Target"] == expected_target
