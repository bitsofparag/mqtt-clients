#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Test script for IoT Thing
# Copyright: © 2021, Parag M.
# See /LICENSE for licensing information.
import argparse
import logging
import os
import ssl
import time
from os import path

import paho.mqtt.client as mqtt

from mqtt_clients.shared import mock_data

here = path.abspath(path.dirname(__file__))
log = logging.getLogger('mqtt_clients')

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
    default=path.join(here, "certs/thing.cert"),
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

message_format = args.message_format
host = args.host
port = args.port
root_ca_path = args.root_ca_path
certificate_path = args.certificate_path
private_key_path = args.private_key_path
client_id = args.thing_name
thing_name = args.thing_name
pub_topic = args.topic or (f"test_broker/{message_format}/publish/testing")
subs_topic = "test_broker/subscribe/"
interval = int(args.interval)
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
        print("exception ssl_alpn()")
        raise e


def __on_connect(client, userdata, flags, rc):
    """Subscribe when the client receives a CONNACK response from the server."""
    log.info("Connected with result code %s" % str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(subs_topic, 0, None)
    client.publish(pub_topic, mock_device_buffer, 0)


# The callback for when a PUBLISH message is received from the server.
def __on_message(client, userdata, msg):
    """Print message when received from the mqtt server."""
    log.info(
        "Received message on topic %s: %s\n" %
        (msg.topic, str(msg.payload)))


def __on_log(self, client, userdata, level, buf):
    log.debug(f"{client}, {userdata}, {level}, {buf}")


def run_mock_device():
    """Simulates a fake device that generates telemetry data."""
    loop_counter = 0
    while True:  # publish loop
        payload = None
        if message_format == "json":
            payload = mock_data.get_json_event(loop_counter)
        if message_format == "protobuf":
            log.info("Not implemented. Stopping device...")
            raise InvalidMessageFormat
        mock_device_buffer.append(payload)
        log.info(f"buffer size: {len(mock_device_buffer)}")
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
    client = mqtt.Client(client_id=client_id)
    ssl_context = __ssl_alpn(root_ca_path, certificate_path, private_key_path)
    #client.tls_set_context(context=ssl_context)
    client.tls_set(root_ca_path, certfile=certificate_path, keyfile=private_key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    client.on_connect = __on_connect
    client.on_message = __on_message
    #client.on_log = __on_log
    client.enable_logger(logger=log)

    # Start connection loop
    try:
        log.info("Trying to connect to %s" % (host))
        conn_res = client.connect(host, port=port, keepalive=120)
        client.loop_start()
        while True:
            client.publish(
                topic=pub_topic,
                payload="hello"
            )
            time.sleep(2)
        #run_mock_device()
    except InvalidMessageFormat as e:
        log.error(f"Message format {message_format} is not valid or unimplemented.")
        client.loop_stop()
        time.sleep(2)
        exit(0)
    except KeyboardInterrupt:
        log.info(f"Closing client...")
        client.loop_stop()
        time.sleep(2)
        exit(0)
    except Exception as e:
        log.error("Type: %s" % str(type(e)))
        client.loop_stop()
        time.sleep(2)
        exit(2)
