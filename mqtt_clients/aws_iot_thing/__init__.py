#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Test script for IoT Thing
# Copyright: © 2021, Parag M.
# See /LICENSE for licensing information.
import argparse
import click
import json
import logging
import os
import ssl
import time
from os import path

import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

from mqtt_clients.shared import mock_data

here = path.abspath(path.dirname(__file__))
log = logging.getLogger('mqtt_clients')

# Click

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--format",
    action="store",
    dest="message_format",
    required=True,
    help="Message format: json, protobuf or collectd", )
parser.add_argument(
    "-e",
    "--endpoint",
    action="store",
    required=True,
    dest="host",
    help="AWS IoT custom endpoint", )
parser.add_argument(
    "-p",
    "--port",
    action="store",
    dest="port",
    default=8883,
    help="Port number of the AWS IoT endpoint", )
parser.add_argument(
    "-r",
    "--rootCA",
    action="store",
    dest="root_ca_path",
    default=path.join(here, "certs/RootCA.pem"),
    help="Root CA file path")
parser.add_argument(
    "-c",
    "--cert",
    action="store",
    dest="certificate_path",
    default=path.join(here, "certs/thing.crt"),
    help="Certificate file path")
parser.add_argument(
    "-k",
    "--key",
    action="store",
    dest="private_key_path",
    default=path.join(here, "certs/thing.key"),
    help="Private key file path")
parser.add_argument(
    "-n",
    "--thing_name",
    action="store",
    dest="thing_name",
    default="test_broker_001",
    help="Targeted thing name", )
parser.add_argument(
    "-t",
    "--topic",
    action="store",
    dest="topic",
    default="",
    help="Targeted topic", )
parser.add_argument(
    "-w",
    "--wait",
    action="store",
    dest="interval",
    default=5,
    help="Time interval to wait between messages.", )

args = parser.parse_args()
if not args.message_format:
    parser.error("Please specify message format, -f json|protobuf")
    exit(2)

if not args.certificate_path or not args.private_key_path:
    parser.error(
        "Missing credentials for authentication, you must specify --cert and --key args."
    )
    exit(2)

if not os.path.isfile(args.root_ca_path):
    parser.error("No root CA found at {}".format(args.root_ca_path))
    exit(3)

if not os.path.isfile(args.certificate_path):
    parser.error("No certificate found at {}".format(args.certificate_path))
    exit(3)

if not os.path.isfile(args.private_key_path):
    parser.error("No private key found at {}".format(args.private_key_path))
    exit(3)

message_format: str = args.message_format
host: str = args.host
port: int = int(args.port)
root_ca_path: str = args.root_ca_path
certificate_path: str = args.certificate_path
private_key_path: str = args.private_key_path
client_id: str = args.thing_name
thing_name: str = args.thing_name
pub_topic: str = args.topic or (f"test_broker/{message_format}/publish/testing")
subs_topic: str = "test_broker/subscribe/"
interval: int = int(args.interval)
mock_device_buffer: list = []


class InvalidMessageFormat(Exception):
    """Raise when message format is invalid or unimplemented"""
    pass


def __ssl_alpn(ca, cert, private):
    """Return ssl context that will be used by the mqtt client."""
    try:
        # debug print opnessl version
        log.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
        ssl_context = ssl.create_default_context()
        # ssl_context.set_alpn_protocols([IoT_protocol_name])
        ssl_context.load_verify_locations(cafile=ca)
        ssl_context.load_cert_chain(certfile=cert, keyfile=private)

        return ssl_context
    except Exception as e:
        log.error(f"SSL Exception in ssl_alpn() : {e}")
        raise e


def __on_connect(client, userdata, flags, rc):
    """Subscribe when the client receives a CONNACK response from the server."""
    log.info(f"Connected with result code {str(rc)}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(subs_topic, 0, None)
    client.publish(pub_topic, mock_device_buffer, 0)


# The callback for when a PUBLISH message is received from the server.
def __on_message(client, userdata, msg):
    """Print message when received from the mqtt server."""
    log.info(f"Received message on topic {msg.topic}: {str(msg.payload)}\n")


def __on_log(self, client, userdata, level, buf):
    log.debug(f"{client}, {userdata}, {level}, {buf}")


def run_mock_device(device):
    """Simulates a fake device that generates telemetry data."""
    loop_counter = 0
    while True:  # publish loop
        payload = None
        if message_format == "json":
            payload = mock_data.get_json_event(loop_counter)
        if message_format == "protobuf":
            log.info("Not implemented. Stopping device...")
            raise InvalidMessageFormat
        # TODO handle buffer cases later
        #mock_device_buffer.append(payload)
        device.publish(pub_topic, payload, 1)
        log.info(f"Published {payload}")
        time.sleep(interval)
        loop_counter += 1


def run_client():
    log.info("--- Input parameters --- ")
    log.info("AWS IoT endpoint : {}:{}".format(host, port))
    log.info("AWS IoT Thing    : {}".format(thing_name))
    log.info("AWS Topic        : {}".format(pub_topic))
    log.info("Private key     : {}".format(private_key_path))
    log.info("Private cert      : {}".format(certificate_path))
    log.info("------------------------ ")

    # Set up the mqtt client
    # Taken from - https://github.com/aws/aws-iot-device-sdk-python#awsiotmqttclient
    client = AWSIoTPyMQTT.AWSIoTMQTTClient(thing_name)
    # Disable metrics collection
    AWSIoTPyMQTT.AWSIoTMQTTClient.disableMetricsCollection(client)
    client.configureEndpoint(host, port)  # TLS auth
    client.configureCredentials(root_ca_path, private_key_path, certificate_path)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec

    # Start connection loop
    try:
        log.info(f"Trying to connect to {host}")
        client.connect()
        run_mock_device(client)
    except InvalidMessageFormat as e:
        log.error(f"Message format {message_format} is not valid or unimplemented.")
        client.disconnect()
        time.sleep(2)
        exit(0)
    except KeyboardInterrupt:
        log.info(f"Closing client...")
        client.disconnect()
        time.sleep(2)
        exit(0)
    except Exception as e:
        log.error(f"Exception: {e}")
        log.error("Type: %s" % str(type(e)))
        client.disconnect()
        time.sleep(2)
        exit(2)
