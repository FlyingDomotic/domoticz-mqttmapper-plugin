#!/usr/bin/python3
#   Dump MqttMapper topic values
#

import glob
from logging import debug
import os
import pathlib
import getopt
import sys
import json
from time import sleep
import paho.mqtt.client as mqtt
import random

# Print an error message
def printError(message):
    print(F"Error: {message}")

# Print an log message
def printLog(message):
    print(F"{message}")

# Print a debug message
def printDebug(message):
    global debugFlag
    if debugFlag:
        print(F"Debug: {message}")

# Returns a dictionary value giving a key or default value if not existing
def getValue(dict, key, default=''):
    if dict == None:
        return default
    else:
        if key in dict:
            if dict[key] == None:
                return default #or None
            else:
                return dict[key]
        else:
            return default #or None

# Called when MQTT broker is connected
def onConnect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode:
        if reasonCode >=0 and reasonCode <= 5:
            errorMessage = ["Ok", \
                "Inccorect protocol version", \
                "Invalid client identifier", \
                "Server unavailable", \
                "Bad username or password", \
                "Not authorized" \
                ][reasonCode]
        else:
            errorMessage = "Unknown error"
        printError(F"Failed to connect - Reason code={reasonCode}/{errorMessage}")
        return
    printDebug(F"Connected to {userdata['host']}:{userdata['port']}")
    mqttTopics = userdata["mqttTopics"]
    printDebug(F"Subscribing to {mqttTopics}")
    status = client.subscribe(mqttTopics)
    printDebug(F"Status={status}")

# Called when a subscription is acknoledged
def onSubcribe(client, userdata, mid, granted_qos):
    pass

# Called when a subscribed message is received
def onMessage(client, userdata, msg):
    # Reset sleep to 2 seconds
    global sleepCount
    sleepCount = 2
    cleanMessage = msg.payload.decode('UTF-8').replace('\n','').replace('\t','')
    printLog(F"{msg.topic}={cleanMessage}")

# Check MqttMapper JSON mapping file jsonConfigurationFile
def dumpTopics(jsonParameters, jsonConfiguration, jsonConfigurationFile):
    # Iterating through the configuration JSON file
    printLog("Reading "+jsonConfigurationFile)

    # Clear topics to subscribe
    mqttTopics = []

    # Scan all configuration lines
    for node in jsonConfiguration.items():
        # Extract topic
        nodeTopic = getValue(node[1], "topic")

        # Trace line (contains definition of device)
        printLog(F"{node}")

        # Add to topic list if not already done
        if nodeTopic not in mqttTopics:
            mqttTopics.append((nodeTopic, 0))

    # Compose unique mqtt client Id
    random.seed()
    mqttClientName = pathlib.Path(__file__).stem+'_{:x}'.format(random.randrange(65535))

    # Create client with userdata
    data = {}
    data["host"] = jsonParameters['mqttHost']
    data["port"] = jsonParameters['mqttPort']
    data["mqttTopics"] = mqttTopics
    mqttClient = mqtt.Client(client_id=mqttClientName, userdata=data)
    printDebug(F"Client {mqttClientName}, topics {mqttTopics}")

    # Set callbacks
    mqttClient.on_message = onMessage
    mqttClient.on_connect = onConnect
    mqttClient.on_subscribe = onSubcribe

    # Set credentials
    if jsonParameters["mqttUsername"] != "":
        if jsonParameters["mqttPassword"] != "":
            printDebug(F"Credentials: Username {jsonParameters['mqttUsername']}, password {jsonParameters['mqttPassword']}")
            mqttClient.username_pw_set(jsonParameters["mqttUsername"], jsonParameters["mqttPassword"])
        else:
            printDebug(F"Credentials: Username {jsonParameters['mqttUsername']}")
            mqttClient.username_pw_set(jsonParameters["mqttUsername"])

    # Set initial sleep count to 10 sec (will be overwritten to 2 on each received message)
    global sleepCount
    sleepCount = 10

    # Connect to MQTT server
    printDebug(F"Opening {jsonParameters['mqttHost']}, port {jsonParameters['mqttPort']}")
    mqttClient.connect(host=jsonParameters["mqttHost"], port=int(jsonParameters["mqttPort"]))

    # Loop MQTT for sleeCount seconds (as told, will be overwritten in onMessage)
    while 1:
        if sleepCount <= 0:
            break
        sleepCount -= 1
        mqttClient.loop(timeout=1.0, max_packets=0)

    # Additional wait if asked (useful for data without retain flag)
    global waitTime
    if waitTime > 0.0:
        printDebug(F"Waiting for {waitTime} minute{'s' if waitTime > 1 else ''}")
        mqttClient.loop(timeout=waitTime * 60.0, max_packets=0)

    # Disconnect
    mqttClient.disconnect()
    # Release client
    mqttClient = None

# *** Main code ***

# Init arguments variables
cdeFile = __file__
if cdeFile[:2] == './':
    cdeFile = cdeFile[2:]

inputFiles = []

global debugFlag
debugFlag = False

global waitTime
waitTime = 0.0

# Use command line if given
if sys.argv[1:]:
    command = sys.argv[1:]
else:
    command = []

# Read arguments
helpMsg = 'Usage: ' + cdeFile + ' [options]' + """
    [--input=<input file(s)>]: input file name (can be repeated, default to *.json.parameters)
    [--wait=<minutes>]: wait for MQTT changes for <minutes>
    [--debug]: print debug messages
    [--help]: print this help message

   Dump MqttMapper topic values

"""
try:
    opts, args = getopt.getopt(command, "h",["help", "debug", "input=", "wait="])
except getopt.GetoptError as excp:
    print(excp.msg)
    print('in >'+str(command)+'<')
    print(helpMsg)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(helpMsg)
        sys.exit()
    elif opt == '--debug':
        debugFlag = True
    elif opt == '--wait':
        waitTime = int(arg)
        printDebug("Will wait for {waitTime} minute(s)")
    elif opt == '--input':
        inputFiles.append(arg)

if not inputFiles:
    inputFiles.append('*.json.parameters')

# Set current working directory to this python file folder
os.chdir(pathlib.Path(__file__).parent.resolve())

# Read config files
for specs in inputFiles:
    for parametersFile in glob.glob(specs):
        jsonParameters = None
        try:
            with open(parametersFile, encoding = 'UTF-8') as parametersStream:
                jsonParameters = json.load(parametersStream)
        except Exception as exception:
            printError(str(exception)+" when loading "+parametersFile+". Please report error")
            continue
        configFile = str(parametersFile).replace(".parameters", "")
        try:
            with open(configFile, encoding = 'UTF-8') as configStream:
                jsonConfig = json.load(configStream)
        except Exception as exception:
            printError(str(exception)+" when loading "+configFile+". Fix error and retry check!!!")
            continue
        dumpTopics(jsonParameters, jsonConfig, configFile)
