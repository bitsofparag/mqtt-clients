import uuid

DEVICES = [
    {
        'name': 'dev-0001',
        'Device ID': 'nrf-test-0001',
        'UID': str(uuid.uuid4()),
        'MAC address': 'fa:cf:d1:79:3e:08',
        'IP address': '192.168.178.162'
    },
    {
        'name': 'dev-0002',
        'Device ID': 'nrf-test-0002',
        'UID': str(uuid.uuid4()),
        'MAC address': '4f:90:54:b5:0f:23',
        'IP address': '10.0.34.45'
    },
    {
        'name': 'dev-0003',
        'Device ID': 'nrf-test-0003',
        'UID': str(uuid.uuid4()),
        'MAC address': 'f4:97:27:10:50:6c',
        'IP address': '192.168.0.50'
    },
    {
        'name': 'dev-0004',
        'Device ID': 'nrf-test-0004',
        'UID': str(uuid.uuid4()),
        'MAC address': 'de:2d:c3:dd:d2:dd',
        'IP address': '10.0.1.100'
    },
    {
        'name': 'dev-0005',
        'mgate': 'nrf-test-0005',
        'UID': str(uuid.uuid4()),
        'MAC address': 'e4:b4:e8:1c:0a:c7',
        'IP address': '192.168.178.34'
    }
]
NUM_DEVICES = len(DEVICES)
