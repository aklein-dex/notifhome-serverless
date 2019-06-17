#!/usr/bin/python
# inspired from: https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617
# Python 2.7
#
# Create a file endpoint.txt containing the URL of your IoT Core.

import paho.mqtt.client as paho
import threading
import Queue
import ssl
import json
import time
import onionGpio # See Library: https://github.com/OnionIoT/onion-gpio
from OmegaExpansion import oledExp # for the OLED screen
from datetime import datetime

AWS_PORT = 8883
CA_PATH = "./certs/AmazonRootCA1.pem"
CERT_PATH = "./certs/notifhomeBoard.pem.crt"
KEY_PATH = "./certs/awsiot.key"

LED_PIN = 0 # GPIO 0
BUTTON_PIN = 1 # GPIO 1

LED_ON = 1
LED_OFF = 0

# IoT topic to listen on
TOPIC = "notifhome"

# Maximum items the queue can contain
QUEUE_MAX_LENGTH = 20

# Contains the endpoint
aws_endpoint = ""

# Contains JSON objects
notificationsQueue = Queue.Queue(QUEUE_MAX_LENGTH)

# Flag telling us if a thread is already running
threadIsRunning = False

# Print out log messages
def print_it(log):
    now = datetime.now()
    nowStr = now.strftime("[%Y/%m/%d %H:%M:%S]")
    print(nowStr + " " + log)

# Triggered when connected to AWS
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print_it("Connected to AWS!")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(TOPIC)
        print_it("Subscribed to topic: " + TOPIC)
    else:
        print_it("Connection refused. Error code: " + str(rc))

# Triggered when losing connection
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print_it("Unexpected disconnection: " + str(rc))

# Triggered when a message arrives from AWS
def on_message(client, userdata, msg):
    print_it("Message received [" + msg.topic + "]: " + str(msg.payload))

    try:
        notification = json.loads(str(msg.payload))

        if notification['message']:
            notificationsQueue.put_nowait(notification)
        else:
            print_it("  Invalid message")
            return
    except Queue.Full:
        print_it("  Queue is full! Notification is ignored")
        return

    if threadIsRunning:
        print_it("  Message queued")
    else:
        thread = threading.Thread(target=process_notifications_queue, args=(1,))
        thread.start()

# Loop through the items in the queue (thread)
def process_notifications_queue(name):
    global threadIsRunning

    threadIsRunning = True
    while True:
        try: 
            notification = notificationsQueue.get_nowait()
            #led.setValue(LED_ON)
            #loop_until_button_is_pressed(notification)
            write_message_to_screen(notification)
            notificationsQueue.task_done()
        except Queue.Empty:
            threadIsRunning = False
            return

# Loop until the button is pressed
def loop_until_button_is_pressed(notification):
    pressed = False
    print_it("Processing: " + notification["message"])
    while not pressed:
        if int(button.getValue()):
            pressed = True
            print_it("Button pressed!")
            led.setValue(LED_OFF)
            time.sleep(2) # Debounce button press
            print_it("End loop")
        time.sleep(0.05)
    print_it("Finished: " + notification["message"])

# Write a message on the OLED screen
def write_message_to_screen(notification):
    now = datetime.now()
    nowStr = now.strftime("%b %d %H:%M:%S")
    ret = oledExp.write(nowStr)
    oledExp.setCursor(3,8)
    ret = oledExp.write(notification["message"])

# Start!
print_it("NOTIFHOME: starting...")
print_it("Press CTRL+C to exit")

# Read the file containing the AWS endpoint
try:
    fileEndpoint = open("endpoint.txt", "r")
    if fileEndpoint.mode == "r":
        aws_endpoint = fileEndpoint.readline().strip()
        print_it("AWS endpoint: " + aws_endpoint)
    else:
        print_it("Unable to read endpoint.txt. Exiting.")
        exit()
finally:
    fileEndpoint.close()

# Setup the OLED screen
oledExp.setVerbosity(0)
status = oledExp.driverInit()
if (status != 0):
    print("Unable to initialize OLED screen")
    exit()

# Setup the led
led = onionGpio.OnionGpio(LED_PIN)
led.setOutputDirection(0) # make LED output and init to 0

# Setup the button
button = onionGpio.OnionGpio(BUTTON_PIN)
button.setInputDirection() # make Button input

# Setup mqttc
mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message
mqttc.tls_set(CA_PATH, certfile=CERT_PATH, keyfile=KEY_PATH, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect to AWS
mqttc.connect(aws_endpoint, AWS_PORT, keepalive=60)

try:
    mqttc.loop_forever()
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly
    print_it("Exiting...")
    oledExp.clear()
#     # Note: _freeGPio() failed to execute...
#     # led._freeGpio()
#     # button._freeGpio()

