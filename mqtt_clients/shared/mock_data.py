import json
import random
from datetime import datetime

from .mock_devices import DEVICES, NUM_DEVICES


def _generate_event_payload(count=None, device_id=None):
    """Create and return mock telemetry data as an event payload object.

    This is the raw telemetry data to be stored.
    """
    event_payload = dict({
        "battery_level": {
            "current_level": random.randint(3000, 3600)
        },
        "temperature": random.randint(10, 30),
        "sensor_status": "ONLINE",
        "rsrp": random.randint(10, 100),
        "rsrq": random.randint(10, 100),
    })

    if count is not None:
        event_payload['messageCount'] = count

    return event_payload


def _generate_event(device_id=None):
    """Create and return a mock event object.

    :param device_id: of the device that is sending data
    """
    event = {}
    now = datetime.now()
    timestamp = int(datetime.timestamp(now))
    # formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%D %H:%M:%S")
    event['timestamp'] = timestamp
    event['device_id'] = device_id
    event['customer_id'] = "acme-test"

    return event


# TODO Make this relevant to batch processing
def get_json_events(count=None):
    """Return AN ARRAY of events in json.

    :param count: an optional number sent from the calling publish loop
    """
    results = []
    for i in range(NUM_DEVICES):
        device_id = DEVICES[i]['name']
        event = _generate_event(device_id=device_id)
        payload = _generate_event_payload(count=count, device_id=device_id)
        event['event_payload'] = payload
        results.append(event)
    return json.dumps(results)


def get_json_event(count=None):
    """Return ONE event in json format.

    :param count: an optional number sent from the calling publish loop
    """
    device_id = random.choice(DEVICES)['name']
    event = _generate_event(device_id=device_id)
    payload = _generate_event_payload(count=count, device_id=device_id)
    event['event_payload'] = payload
    return json.dumps(event)
