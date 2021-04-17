"""
MQTT Clients.
~~~~~~~~~~~~~~~~~~~~~

MQTT Clients in Python

Basic usage:
    >>> import mqtt_clients
    >>> mqtt_clients()

:copyright: (c) 2021 Parag M.
:license: MIT, see LICENSE for more details.
"""
import logging
import sys
from os import path

from decouple import config

from mqtt_clients.aws_iot_thing import run_client

SETTINGS = dict()
SENTRY_DSN = config('SENTRY_DSN', default=False)
here = path.abspath(path.dirname(__file__))
logging.basicConfig(format='%(levelname)s - %(message)s', stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger('mqtt_clients')

# Sentry integration
if (SENTRY_DSN):
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.WARNING,  # Capture warnings and above as breadcrumbs
        event_level=logging.ERROR
    )  # Send errors as events
    # if environment is staging or production, enable sentry
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging])


def main(*args, **kwargs):
    """Print hello world.

    :some_arg type: describe the argument `some_arg`
    """
    logger.debug('Hello world!')
    run_client()


if __name__ == '__main__':
    main()
