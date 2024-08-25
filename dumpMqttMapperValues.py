#!/usr/bin/python3
#
#   Dump MqttMapper values
#
#   This tool dumps MQTT Mapper data from:
#       - JSON configuration file
#       - Domoticz API
#       - Domoticz database
#       - MQTT retained topics
#
#   It also checks for database duplicated names (that causes amazing side effects ;-)
#
#   Flying Domotic - https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin
#

codeVersion = "1.1.0"

import os
import sys
import pathlib
import getopt
import glob
import json
import random
import requests

# MQTT import stuff
global mqttInstalled
mqttInstalled = False

global mqttApiVersion
mqttApiVersion = 1

# Try to load paho-mqtt
try:
    import paho.mqtt.client as mqtt
    mqttInstalled = True
    # Try to find CallbackAPIVersion (exists starting on version 2)
    try:
        from paho.mqtt.enums import CallbackAPIVersion
        mqttApiVersion = 2
    except AttributeError:
        pass
except:
    pass

# Sqlite3 import stuff
global sqlite3Installed
sqlite3Installed = False

# Try to load sqlite3
try:
    import sqlite3
    sqlite3Installed = True
except:
    pass

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

# Checks for duplicates device (ending) names in database
def checkForDatabaseDuplicates(databaseConnection):
    if databaseConnection != None:
        cursor = databaseConnection.cursor()
        datas = cursor.execute("select d.ID, d.Name, h.Name from DeviceStatus d, Hardware H where h.ID = D.HardwareID;").fetchall()
        deviceNames = {}
        for data in datas:
            deviceIdx = data[0]
            deviceName = data[1]
            hardwareName = data[2]
            for key in deviceNames.keys():
                if key == deviceName:
                    printError(F"Device '{deviceIdx}'/'{hardwareName}' and '{deviceNames[key]['idx']}'/'{deviceNames[key]['hardware']}' are both nammed '{deviceName}' - Problems likely to occur!")
                elif checkSameEnd and (key.endswith(deviceName) or deviceName.endswith(key)):
                    printLog(F"Warning: Device '{deviceIdx}'/'{hardwareName}', name '{deviceName}' and '{deviceNames[key]['idx']}'/'{deviceNames[key]['hardware']}', name '{key}' '{deviceName}' share same end - Amazing things may happen...")
            # Save this device data
            fields = {}
            fields["idx"] = deviceIdx
            fields["hardware"] = hardwareName
            deviceNames[deviceName] = fields

# Called when MQTT broker is connected
def onConnect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode != 'Success':
        printError(F"Failed to connect - Reason code={reasonCode}")
        return
    printDebug(F"Connected to {userdata['host']}:{userdata['port']}")
    mqttTopics = userdata["mqttTopics"]
    printDebug(F"Subscribing to {mqttTopics}")
    status = client.subscribe(mqttTopics)
    printDebug(F"Status={status}")

# Called when a subscription is acknoledged
def onSubcribe(client, userdata, mid, reason_codes, properties=None):
    pass

# Called when a subscribed message is received
def onMessage(client, userdata, msg):
    # Reset sleep to 2 seconds
    global sleepCount
    sleepCount = 2
    cleanMessage = msg.payload.decode('UTF-8').replace('\n','').replace('\t','')
    printLog(F"Topic '{msg.topic}'='{cleanMessage}'")

# Check MqttMapper JSON mapping file jsonConfigurationFile
def dumpTopics(jsonParameters, jsonConfiguration, jsonConfigurationFile):
    # Iterating through the configuration JSON file
    printLog(F"Reading {jsonConfigurationFile}")

    # Clear topics to subscribe
    mqttTopics = []

    # Scan all configuration lines
    for node in jsonConfiguration.items():
        deviceName = node[0]
        mqttMapperDefinition = node[1]

        # Extract topic and key
        nodeTopic = getValue(mqttMapperDefinition, "topic")
        nodeKey = getValue(mqttMapperDefinition, "key")
        # build device ID
        deviceId = nodeKey if nodeKey !="" else nodeTopic

        apiDefinition = getApiDataById(deviceId, "    API: " )
        databaseDefinition = getDatabaseDataById(deviceId, "    Database: ")
    
        printLog(F"{deviceName}")
        printLog(F"    MqttMapper: {mqttMapperDefinition}")
        if apiDefinition != "": 
            printLog(F"{apiDefinition}")
        if databaseDefinition != "": 
            printLog(F"{databaseDefinition}")

        # Extract topic
        nodeTopic = getValue(mqttMapperDefinition, "topic")
        # Add to topic list if not already done
        if nodeTopic not in mqttTopics:
            mqttTopics.append((nodeTopic, 0))

    global mqttInstalled
    if mqttInstalled:
        # Compose unique MQTT client Id
        random.seed()
        mqttClientName = pathlib.Path(__file__).stem+'_{:x}'.format(random.randrange(65535))

        # Create client with userdata
        data = {}
        data["host"] = jsonParameters['mqttHost']
        data["port"] = jsonParameters['mqttPort']
        data["mqttTopics"] = mqttTopics
        if mqttApiVersion >= 2:
            mqttClient = mqtt.Client(client_id=mqttClientName, userdata=data, callback_api_version=CallbackAPIVersion.VERSION2)
        else:
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
            mqttClient.loop(timeout=1.0)

        # Additional wait if asked (useful for data without retain flag)
        global waitTime
        if waitTime > 0.0:
            printDebug(F"Waiting for {waitTime} minute{'s' if waitTime > 1 else ''}")
            mqttClient.loop(timeout=waitTime * 60.0)

        # Disconnect
        mqttClient.disconnect()
        # Release client
        mqttClient = None

# Return an URL text content
def getLinkContent(url):
    try:
        response = requests.get(url)
    except Exception as exception:
        return F"Error {str(exception)} when opening {url}", None
    else:
        if response.status_code != 200:
            return F"{url} returned error {response.status_code}", response.text
    return None, response.text

# Return an URL binary content
def getLinkBinaryContent(url):
    try:
        response = requests.get(url)
    except Exception as exception:
        return F"Error {str(exception)} when opening {url}", None
    else:
        if response.status_code != 200:
            return F"{url} returned error {response.status_code}", response.text
    return None, response.content

# Return a json dictionary containing decoded URL content
def getJsonLinkContent(url):
    errorMessage, response = getLinkContent(url)
    if errorMessage == None and response != None:
        try:
            jsonContent = json.loads(response)
            return None, jsonContent
        except Exception as exception:
            return F"Error {str(exception)} when decoding response from {url}", response
    else:
        return errorMessage, response

# Check if new API is used
def isNewApi(version):
    return version[:2] == "20" and version >= "2023.2"

# Extract data from database using device ID
def getDatabaseDataById(deviceId, prefix):
    global databaseConnection
    if databaseConnection != None:
        cursor = databaseConnection.cursor()
        datas = cursor.execute(F"select ID, Type, SubType, SwitchType, nValue, sValue, LastLeveL, Color, Name from DeviceStatus where DeviceID='{deviceId}'").fetchall()
        response = ""
        if len(datas) > 0:
            for data in datas:
                response += F"\n{prefix}" \
                    + F"Name='{data[8]}'" \
                    + F", Idx='{data[0]}'" \
                    + F", Type='{data[1]}|{data[2]}|{data[3]}'" \
                    + F", nValue='{data[4]}'" \
                    + F", sValue='{data[5]}'" \
                    + F", Color='{data[7]}'" \
                    + F", LastLevel='{data[6]}'" 
            cursor.close()
            return response[1:]
        else:
            cursor.close()
            return F"{prefix}'Device ID {deviceId}' not found"
    return ""

# Extract data by device ID from Domoticz device list
def getApiDataById(deviceId, prefix):
    global domoticzDevices
    if domoticzDevices != None:
        result = getValue(domoticzDevices, "result")
        if result != "":
            response = ""
            for device in result:    
                if getValue(device, "ID") == deviceId:
                    response += F"\n{prefix}" \
                        + F"Name='{getValue(device, 'Name')}'" \
                        + F", Idx='{getValue(device, 'idx')}'" \
                        + F", Type='{getValue(device, 'Type')}|{getValue(device, 'Subtype')}|{getValue(device, 'Switchtype')}'" \
                        + F", Data='{getValue(device, 'Data')}'" \
                        + F", Color='{getValue(device, 'Color')}'" \
                        + F", Level='{getValue(device, 'Level')}'"
            if response != "":
                return response[1:]
            return F"{prefix} Device ID '{deviceId}' not found"
    return ""

# *****************
# *** Main code ***
# *****************

# Welcome message
print(F"Starting dumpMqttMapperValues V{codeVersion}")

# Init arguments variables
cdeFile = __file__
if cdeFile[:2] == './':
    cdeFile = cdeFile[2:]

inputFiles = []
domoticzUrl = None
global debugFlag
debugFlag = False

keepFlag = False
checkSameEnd = False

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
    [--url=<domoticz URL>: use this Domoticz URL instead of default http://127.0.0.1:8080/]
    [--checkend]: check for device names sharing same text at end
    [--keep]: keep database copy and API response
    [--debug]: print debug messages
    [--help]: print this help message

   Dump MqttMapper topic values

"""
try:
    opts, args = getopt.getopt(command, "h",["help", "debug", "keep", "checkend", "input=", "wait=", "url="])
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
    elif opt == '--keep':
        keepFlag = True
    elif opt == '--sameend':
        checkSameEnd = True
    elif opt == '--url':
        domoticzUrl = arg
    elif opt == '--wait':
        waitTime = int(arg)
        printDebug(F"Will wait for {waitTime} minute(s)")
    elif opt == '--input':
        inputFiles.append(arg)

if not inputFiles:
    inputFiles.append('*.json.parameters')

if domoticzUrl == None:
    domoticzUrl = "http://127.0.0.1:8080/"
    domoticzUrl = "http://Noailles:8080/"

# Check for MQTT installed
if not mqttInstalled:
    printLog(F"Warning: Python MQTT not installed. Please use 'pip3 install paho-mqtt' to fix it")
    printLog(F"Warning: MQTT topics content will not being displayed")

# Set current working directory to this python file folder
os.chdir(pathlib.Path(__file__).parent.resolve())

# Ask for domoticz API version and device list 
domoticzVersion = None

global domoticzDevices
domoticzDevices = None

# Ask Domoticz for version
printDebug(F"Asking for Domoticz version")
errorMessage, jsonContent = getJsonLinkContent(F"{domoticzUrl}json.htm?type=command&param=getversion")

# Ask for Domoticz device list
if errorMessage == None:
    domoticzVersion = jsonContent["version"]
    printDebug(F"Asking for Domoticz API device list for version V{domoticzVersion}")
    if isNewApi(domoticzVersion):
        errorMessage, domoticzDevices = getJsonLinkContent(F"{domoticzUrl}json.htm?type=command&param=getdevices&displayhidden=1")
    else:
        errorMessage, domoticzDevices = getJsonLinkContent(F"{domoticzUrl}json.htm?type=devices&displayhidden=1")

# Print errors if any
if errorMessage != None:
    printLog(F"Warning: {errorMessage}")

# Display a warning if something wrong
if domoticzVersion == None or domoticzDevices == None:
    printLog(F"Warning: Domoticz API device content will not be displayed")

apiFileName = "kept_apiAnswer.json"
# Keep a copy of API answer if needed
if domoticzDevices != None and keepFlag:
    try:
        with open(apiFileName, "wt") as f:
            f.write(json.dumps(domoticzDevices, indent=4))
    except Exception as exception:
        printError(F"Error {str(exception)} when writting {apiFileName} - Continuing...")

databaseFileName = "kept_databaseCopy.db"

global databaseConnection
databaseConnection = None

# Check sqlite3 installed
if sqlite3Installed:
    printDebug(F"Asking for Domoticz database copy")
    # Ask Domoticz for a database copy
    errorMessage, binaryContent = getLinkBinaryContent(F"{domoticzUrl}backupdatabase.php")
    if errorMessage == None and binaryContent != "":
        try:
            with open(databaseFileName, "wb") as dbStream:
                dbStream.write(binaryContent)
        except Exception as exception:
            errorMessage = str(exception)+" when writing "+databaseFileName
            
    # Open database
    if errorMessage == None:
        try:
            # Open database copy
            databaseConnection = sqlite3.connect(databaseFileName)
        except Exception as exception:
            errorMessage = str(exception)+" when opening "+databaseFileName

    # Print errors if any
    if errorMessage != None:
        printLog(F"Warning: {errorMessage}")
else:
        printLog(F"Warning: Python sqlite3 not installed. Please use 'pip3 install sqlite3' to fix it")


# Display a warning if something wrong
if databaseConnection == None:
    printLog(F"Warning: Domoticz database device content will not be displayed")

# Read config files
for specs in inputFiles:
    for parametersFile in glob.glob(specs):
        jsonParameters = None
        try:
            with open(parametersFile, encoding = 'UTF-8') as parametersStream:
                jsonParameters = json.load(parametersStream)
        except Exception as exception:
            printError(F"{str(exception)} when loading {parametersFile}. Please report error")
            continue
        configFile = str(parametersFile).replace(".parameters", "")
        try:
            with open(configFile, encoding = 'UTF-8') as configStream:
                jsonConfig = json.load(configStream)
        except Exception as exception:
            printError(F"{str(exception)} when decoding {configFile}. Fix error and retry check!!!")
            continue
        dumpTopics(jsonParameters, jsonConfig, configFile)

# Close database if needed
if databaseConnection != None:
    printDebug(F"Checking for database duplicates")
    checkForDatabaseDuplicates(databaseConnection)
    databaseConnection.close()

# Should we keep files?
if not keepFlag:
    # Delete api file if it exists, ignoring errors
    if os.path.exists(apiFileName):
        try:
            os.remove(apiFileName)
        except:
            pass
    # Delete database file if it exists, ignoring errors
    if os.path.exists(databaseFileName):
        try:
            os.remove(databaseFileName)
        except:
            pass
