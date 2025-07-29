from my_aws_helpers.event import Event, EventStatus
import pytest


def test_event():
    event = Event(status=EventStatus.success.value, message="test event")
    assert event != None

def test_event_wrong_status():
    with pytest.raises(Exception):
        Event(status="not success", message="test event")

def test_serialiser():
    event = Event(status=EventStatus.success.value, message="test event")
    dynamo_repr = event._to_dynamo_representation()

    assert dynamo_repr['pk'] == f"id##{event.id}"
    assert dynamo_repr['sk'] == f"id##{event.id}"

    obj = Event._from_dynamo_representation(obj = dynamo_repr)

    assert isinstance(obj, Event) == True
        
