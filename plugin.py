# MqttMapper is a Domoticz Python plug in allowing to map MQTT topics directly to Domoticz devices.
#
#   If you want to be able to read/write some MQTT topics and maps them to Domoticz devices, without having to install NodeRed,
#       and/or integrate sensors that don't have HomeAssistant discovery item, this plug-in is made for you.
#
# MqttMapper est un plugin Domoticz qui permet de relier des dispositifs Domoticz à MQTT directement.
#
#   Si vous voulez lire/écrire des topics MQTT et les lier à des dispositifs Domoticz, sans avoir besoin d'installer NodeRed,
#       et/ou intégrer des capteurs qui n'ont pas de découvertes HomeAssistant, ce plug-in est fait pour vous.
#
#   Flying Domotic - https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin
"""
<plugin key="MqttMapper" name="MQTT mapper with network interface" author="Flying Domotic" version="25.6.24-1" externallink="https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin">
    <description>
        MQTT mapper plug-in<br/><br/>
        Maps MQTT topics to Domoticz devices<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" password="true"/>
        <param field="Mode1" label="JSON mapping file to use" width="300px" required="true" default="MqttMapper.json"/>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="Extra verbose" value="Verbose+"/>
                <option label="Verbose" value="Verbose"/>
                <option label="Normal" value="Debug"/>
                <option label="None" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""

#   -----------------------------------------
#   ---------------- Imports ----------------
#   -----------------------------------------

import Domoticz
import json
import time
import subprocess
import os
from typing import Any
from datetime import datetime, timezone
from DomoticzTypes import DomoticzTypes

# Used by VsCodium when running outside Domoticz environment
#   to simulate internal Domoticz functions/variables definition
try:
    from Domoticz import *
except:
    pass

#   ---------------------------------------------------
#   ---------------- MQTT client class ----------------
#   ---------------------------------------------------

class MqttClient:
    Address = ""
    Port = ""
    mqttConn = None
    mqttConnectedCb = None
    mqttDisconnectedCb = None
    mqttPublishCb = None

    #Initialization
    def __init__(self, destination, port, mqttConnectedCb, mqttDisconnectedCb, mqttPublishCb, mqttSubackCb):
        Domoticz.Debug(F"MqttClient::__init__")
        self.Address = destination
        self.Port = port
        self.mqttConnectedCb = mqttConnectedCb
        self.mqttDisconnectedCb = mqttDisconnectedCb
        self.mqttPublishCb = mqttPublishCb
        self.mqttSubackCb = mqttSubackCb
        self.Open()

    # Default value
    def __str__(self):
        Domoticz.Debug(F"MqttClient::__str__")
        if (self.mqttConn != None):
            return str(self.mqttConn)
        else:
            return "None"

    # Open MQTT connection
    def Open(self):
        if (self.mqttConn != None):
            self.Close()
        self.isConnected = False
        self.mqttConn = Domoticz.Connection(Name=self.Address, Transport="TCP/IP", Protocol="MQTT", Address=self.Address, Port=self.Port)
        self.mqttConn.Connect()

    # Send a Ping to keep connection opened
    def Ping(self):
        #Domoticz.Debug(F"MqttClient::Ping")
        if (self.mqttConn != None and self.isConnected):
            self.mqttConn.Send({'Verb': 'PING'})

    # Publish a payload into a topic
    def Publish(self, topic, payload, retain = 0):
        if (self.mqttConn == None or not self.isConnected):
            Domoticz.Error(F"MqttCLient::MQTT not connected, can't Publish {topic}={payload}, retain={retain}")
        else:
            Domoticz.Debug(F"MqttClient::Publish {topic}={payload}, retain={retain}")
            self.mqttConn.Send({'Verb': 'PUBLISH', 'Topic': topic, 'Payload': bytearray(payload, 'utf-8'), 'Retain': retain})

    # Subscribe to a topic (or list of topics)
    def Subscribe(self, topics):
        subscriptionlist = []
        for topic in topics:
            subscriptionlist.append({'Topic':topic, 'QoS':0})
        if (self.mqttConn == None or not self.isConnected):
            Domoticz.Error(F"MqttClient::MQTT not connected, can't Subscribe {subscriptionlist}")
        else:
            Domoticz.Debug(F"MqttClient::Subscribe to {subscriptionlist}")
            self.mqttConn.Send({'Verb': 'SUBSCRIBE', 'Topics': subscriptionlist})

    # Close MQTT connection
    def Close(self):
        Domoticz.Log(F"MqttClient::Close")
        self.isConnected = False
        if self.mqttConn != None:
            if self.mqttConn.Connected():
                self.mqttConn.Disconnect()
        self.mqttConn = None

    # MQTT connected callback
    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug(F"MqttClient::onConnect")
        if (Status == 0):
            ID = F"Domoticz_{Parameters['Key']}_{Parameters['HardwareID']}_{int(time.time())}"
            Domoticz.Log(F"MqttClient::onConnect connect to {Connection.Address}:{Connection.Port}, ID={ID}")
            if self.mqttConn != None:
                self.mqttConn.Send({'Verb': 'CONNECT', 'ID': ID})
            else:
                Domoticz.Error(F"MqttClient::onConnect, not connected...")
        else:
            Domoticz.Error(F"Mqtt::onConnect Failed to connect to  {Connection.Address}:{Connection.Port}, Description: {Description}")

    # MQTT disconnected callback
    def onDisconnect(self, Connection):
        Domoticz.Log(F"MqttClient::onDisconnect Disconnected from  {Connection.Address}:{Connection.Port}")
        self.isConnected = False
        self.Close()
        if self.mqttDisconnectedCb != None:
            self.mqttDisconnectedCb()

    # MQTT message received callback
    def onMessage(self, Connection, Data):
        topic = ''
        if 'Topic' in Data:
            topic = Data['Topic']
        payloadStr = ''
        if 'Payload' in Data:
            payloadStr = Data['Payload'].decode('utf8','replace')
            payloadStr = str(payloadStr.encode('unicode_escape'))

        if Data['Verb'] == "CONNACK":
            self.isConnected = True
            if self.mqttConnectedCb != None:
                self.mqttConnectedCb()

        if Data['Verb'] == "SUBACK":
            if self.mqttSubackCb != None:
                self.mqttSubackCb()

        if Data['Verb'] == "PUBLISH":
            if self.mqttPublishCb != None:
                self.mqttPublishCb(topic, Data['Payload'])

#   ----------------------------------------------------------
#   ---------------- Plug-in base class class ----------------
#   ----------------------------------------------------------

class BasePlugin:
    # MQTT settings
    mqttClient = None
    mqttserveraddress = ""
    mqttserverport = ""
    debugging = "Normal"
    throttleLastDate = {}
    throttleData = {}
    lastHeartbeatUtc = 0
    lastMqttCheckUtc = 0
    jsonData = None
    initDone = False
    switchTypes = DomoticzTypes()

    # Executed on plug-in connection
    def onConnect(self, Connection, Status, Description):
        # Exit if init not properly done
        if not self.initDone or self.mqttClient == None:
            return
        self.mqttClient.onConnect(Connection, Status, Description)

    # Executed on plug-in disconnection
    def onDisconnect(self, Connection):
        # Exit if init not properly done
        if not self.initDone or self.mqttClient == None:
            return
        self.mqttClient.onDisconnect(Connection)

    # Executed on plug-in message reception
    def onMessage(self, Connection, Data):
        # Exit if init not properly done
        if not self.initDone or self.mqttClient == None:
            return
        self.mqttClient.onMessage(Connection, Data)

    # Executed on MQTT connection
    def onMQTTConnected(self):
        # Exit if init not properly done
        if not self.initDone or self.mqttClient == None:
            return
        Domoticz.Debug(F"onMQTTConnected")
        self.mqttClient.Subscribe(self.getTopics())

    # Executed on MQTT disconnection
    def onMQTTDisconnected(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Debug(F"onMQTTDisconnected")

    # Executed on MQTT subscribtion
    def onMQTTSubscribed(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        # (Re)subscribed, refresh device info
        Domoticz.Debug(F"onMQTTSubscribed")

    # Executed when a device is added
    def onDeviceAdded(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Log(F"onDeviceAdded {self.deviceStr(Unit)}")

    # Executed when a device is modified
    def onDeviceModified(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        device = Devices[Unit]
        Domoticz.Log(F"onDeviceModified {self.deviceStr(Unit)}, {device.DeviceID}, nValue={device.nValue}, sValue={device.sValue}")

    # Executed when a device is removed
    def onDeviceRemoved(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Log(F"onDeviceRemoved {self.deviceStr(Unit)}")

    # Find a device by name in devices table
    def getDevice(self, deviceName):
        for device in Devices:
            if (Devices[device].DeviceID == deviceName) :
                # Return device
                return Devices[device]
        # Return None if not found
        return None

    # Get next free device Id
    def getNextDeviceId(self):
        nextDeviceId = 1
        while True:
            exists = False
            for device in Devices:
                if (device == nextDeviceId) :
                    exists = True
                    break
            if (not exists):
                break;
            nextDeviceId = nextDeviceId + 1
        return nextDeviceId

    # Converts a value to boolean (return True for some string values, integer or float different of zero, false else)
    def convertToBool(self, val):
        valType = type(val).__name__
        if valType == "str":
            if val.lower() in ['y', 'yes', 't', 'true', 'on']:
                return True
        elif valType == "int":
            return valType != 0
        elif valType == "float":
            return valType != 0.0
        return False

    # Returns a dictionary value giving a key or default value if not existing
    def getValue(self, dict, key, default: Any =''):
        if dict == None:
            return default
        else:
            if key in dict:
                if dict[key] == None:
                    return default
                else:
                    return dict[key]
            else:
                return default

    # Return value of a key in a list of dictionary, or default value if not found in all dictionaries
    def getValueInDictList(self, dictList, key, default: Any =''):
        for dict in dictList:
            if dict != None:
                if key in dict:
                    if dict[key] != None:
                        return dict[key]
        return default

    # Return a path in a dictionary or default value if not existing
    #   When value is a list, [sub]path can be either "*" to test all list elements, or a numerical index, starting from 1)
    def getPathValue (self, dict, path, separator = '/', default: Any =''):
        try:
            pathElements = path.split(separator)                    # Split path with separator
            pathElement = pathElements[0]                           # Extract first part of path
            if len(pathElements) > 1:                               # Do we have remaining path?
                pathRemaining = separator.join(pathElements[1:])    # Yes, build it, removing first one
            else:
                pathRemaining = ""                                  # No, set empty
            element = dict                                          # Load data
            if type(element).__name__ == "list":                    # Is data a list?
                if pathElement == "*":                              # Yes, do we have a star?
                    found = False                                   # No item found yet
                    for subElement in element:                      # Scan all elements for token
                        result = self.getPathValue(subElement,pathRemaining, separator, None)
                        if result != None:                          # We found a match
                            element = result                        # Load result
                            pathRemaining = ""                      # Clean path as we already have the result
                            found = True                            # Set found flag
                            break                                   # Exit loop
                    if not found:                                   # If nothing found
                        return default                              # Return default
                else:                                               # We have a list with an index
                    index = int(pathElement)                        # Extract list index from path
                    if index < 1 or index > len(element):           # Check it
                        return default                              # Bad index
                    element = element[index-1]                      # Extract data giving index
            else:                                                   # We don't have a list (but a dict)
                if pathElement not in element:                      # Check for path in data
                    return default                                  # Not found, return default
                element = element[pathElement]                      # Extract data
            if pathRemaining != "":                                 # Do we still have remaining path?
                element = self.getPathValue(element, pathRemaining, separator, default) # Iterate
        except:
            element = default
        return element

    # Return True is valueToTest can be interpreted as a float
    def isFloat(self, valueToTest):
        if valueToTest is None:
            return False
        if type(valueToTest).__name__ in ["bool", "dict", "list"]:
            return False
        if type(valueToTest).__name__ in ["int", "float"]:
            return True
        if valueToTest.lower() in ["false", "true", "y", "n", "yes", "no", "on", "off"]:
            return False
        try:
            float(valueToTest)
            return True
        except ValueError:
            return False

    # Return value to use, depending on 'multiplier' and 'digits' for numerical data
    #   If setMapping is specified, we're about to set the value.
    #   Multiplier and/or digits should be taken from setMapping first, if they exists.
    #   Else, they'll be taken from nodeMapping
    #   If multiplier/digit contains a list separated by ";", then itemNumber is used as index
    def computeValue(self, itemValue, nodeMapping, itemNumber, setMapping=None):
        if self.isFloat(itemValue):                                 # If raw value is numeric or float
            result = float(itemValue)                               # Convert value as float
            if int(result) == result:                               # Is value an integer?
                result = int(result)                                # Force to integer
            multiplier = None
            digits = None
            if setMapping:                                          # Are we in set operation?
                multiplier = self.getValue(setMapping, 'multiplier', None)  # Extract multiplier from set parameters
                digits = self.getValue(setMapping, 'digits', None)  # Extract number of digits needed from mapping parameters
            if multiplier == None:                                  # Multiplier not given in setMapping
                multiplier = self.getValue(nodeMapping, 'multiplier', None) # Extract multiplier from node parameters
            if multiplier !=None:                                   # Do we have a multiplier?
                if type(multiplier).__name__ == "str":              # Is multiplier a string?
                    parts = multiplier.split(";")                   # Split string giving ";"
                    if itemNumber < len(parts):                     # Is itemNumber within parts?
                        multiplier = float(parts[itemNumber])       # Isolate this part and use it as multiplier
                if setMapping:                                      # Is this a set operation?
                    result /= float(multiplier)                     # Yes, divide by multiplier
                else:
                    result *= float(multiplier)                     # No, multiply
            if digits == None:                                      # Digits not given in setMapping
                digits = self.getValue(nodeMapping, 'digits', None) # Extract digits from node parameters
            if digits == None:                                      # Digits not defined elsewhere
                return result                                       # Return float not rounded
            if type(digits).__name__ == "str":                      # Is digits a string?
                parts = digits.split(";")                           # Split string giving ";"
                if itemNumber < len(parts):                         # Is itemNumber within parts?
                    digits = parts[itemNumber]                      # Isolate this part and use it as digits
            if int(digits) <= 0:                                    # Digits is negative or zero
                return int(result)                                  # Return integer
            else:                                                   # Digits defined and positive
                return round(result, int(digits))                   # Return rounded value
        else:                                                       # Value is not numerical
            return itemValue                                        # Return original value else

    # Return True if a message matches
    def itemFoundInMessage(self, nodeSelect, message, nodeName):
        selectItem = self.getValue(nodeSelect, 'item', None)        # Get select item
        selectValue = self.getValue(nodeSelect, 'value', None)      # Get select value
        if selectItem == None or selectValue == None:               # Any error?
            Domoticz.Error(F"Key 'select' should have both 'item' and 'value' defined in {nodeSelect} for {nodeName}")
            return False
        else:
            selectItemValue = self.getPathValue(message, selectItem, '/', None) # Extract select value from message
            if selectItemValue == None:
                Domoticz.Error(F"Can't find '{selectItem}' in message for {nodeName}")
                return False
            else:
                if type(selectValue).__name__ == "list":            # Value is a list
                    if selectItemValue not in selectValue:
                        Domoticz.Log(F"'{selectItem}' is '{selectItemValue}' instead of '{selectValue}' for {nodeName}")
                        return False
                else:                                               # Value is not a list
                    if selectItemValue != selectValue:
                        Domoticz.Log(F"'{selectItem}' is '{selectItemValue}' instead of '{selectValue}' for {nodeName}")
                        return False
        return True

    # Return True if a message don't matches
    def itemNotFoundInMessage(self, nodeReject, message, nodeName):
        rejectItem = self.getValue(nodeReject, 'item', None)        # Get reject item
        rejectValue = self.getValue(nodeReject, 'value', None)      # Get reject value
        if rejectItem == None or rejectValue == None:               # Any error?
            Domoticz.Error(F"Key 'reject' should have both 'item' and 'value' defined in {nodeReject} for {nodeName}")
            return False
        else:
            rejectItemValue = self.getPathValue(message, rejectItem, '/', None) # Extract reject value from message
            if rejectItemValue == None:
                Domoticz.Error(F"Can't find '{rejectItem}' in message for {nodeName}")
                return False
            else:
                if type(rejectValue).__name__ == "list":            # Value is a list
                    if rejectItemValue in rejectValue:
                        Domoticz.Log(F"'{rejectItem}' is '{rejectItemValue}' for {nodeName}")
                        return False
                else:                                               # Value is not a list
                    if rejectItemValue == rejectValue:
                        Domoticz.Log(F"'{rejectItem}' is '{rejectItemValue}' for {nodeName}")
                        return False
        return True

    # Return data definition for a given device
    def getDeviceDefinition(self, device):
        # Iterating through the JSON list
        if self.jsonData != None:
            for node in self.jsonData.items():
                nodeItems = node[1]
                nodeTopic = self.getValue(nodeItems, 'topic', None) # Get MQTT topic
                nodeKey = self.getValue(nodeItems, 'key', nodeTopic)# Get device key
                if device.DeviceID == nodeKey:                      # Is this the right topic?
                    return nodeItems                                # Yes, return definition
        return None

    # Execute a local command
    def executeCommand(self, command):
        Domoticz.Log(F"Executing {command}")
        localProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if localProcess.stdout != None:
            for line in localProcess.stdout.readlines():            # Copy all stdout and/or stderr lines to log
                Domoticz.Log(F'>{line.decode("utf-8")}')
        finalStatus = localProcess.wait()                           # Get final status
        if (finalStatus):                                           # Did we got an error?
            Domoticz.Error(F"Error {finalStatus} executing {command}")

    # Format device name
    def deviceStr(self, unit):
        name = "<UNKNOWN>"
        if unit in Devices:
            name = Devices[unit].Name
        return format(unit, '03d') + "/" + name

    # Returns list of topics to subscribe to
    def getTopics(self):
        topics = set()
        # Go through JSON file to extract topics
        if self.jsonData != None:
            for node in self.jsonData.items():
                nodeItems = node[1]
                nodeTopic = self.getValue(nodeItems, 'topic', None)
                # Add topic if not already in list (as multiple devices on the same topic are allowed)
                if nodeTopic not in topics:
                    topics.add(nodeTopic)
        Domoticz.Debug(F"getTopics: '{topics}'")
        return list(topics)

    # Dump plug-in configuration to log
    def dumpConfigToLog(self):
        for x in Parameters:
            if Parameters[x] != "":
                Domoticz.Log(F"'{x}': '{Parameters[x]}'")
        Domoticz.Log(F"Device count: {str(len(Devices))}")
        for x in Devices:
            Domoticz.Log(F"Device: {x} - {str(Devices[x])}")

    # Dump MQTT received message to log
    def dumpMQTTMessageToLog(self, topic, rawmessage, prefix=''):
        message = rawmessage.decode('utf8','replace')
        message = str(message.encode('unicode_escape'))
        Domoticz.Log(F"{prefix}{topic}: '{message}'")

    # Check if a token is present in root device or in one of its sub device
    def hasTokenPresent(self, nodeItems, itemName):
        # Does item exist in nodeItems?
        if itemName in nodeItems:
            return True
        # Scan all sub devices
        subDevices = self.getValue(nodeItems, "subdevices", {})
        for subDeviceKey in subDevices:
            # Does item exist in this sub device?
            if itemName in subDevices[subDeviceKey]:
                return True
        # Nothing found
        return False

    # Return a list with different values of an item name in a device and all its sub devices
    def getValuesList(self, nodeItems, itemName):
        returnList = []
        if itemName in nodeItems:
            returnList.append(nodeItems[itemName])
        # Scan all sub devices
        subDevices = self.getValue(nodeItems, "subdevices", {})
        for subDeviceKey in subDevices:
            # Does item exist in this sub device?
            subDevice = subDevices[subDeviceKey]
            if itemName in subDevice and subDevice[itemName]:
                returnList.append(subDevice[itemName])
        return returnList

    # Return device unit givine a device name
    def getUnit(self, device):
        unit = -1
        for k, dev in Devices.items():
            if dev == device:
                unit = k
        return unit

    # Return True if mappingdimmer is found at node or set level
    def hasMappingDimmer(self, nodeItems: dict) -> bool:
        setItems = self.getValue(nodeItems, "set", None)
        return self.getValue(nodeItems, "mappingdimmer", None) != None \
            or self.getValue(setItems, "mappingdimmer", None) != None

    # Send a pending throttled message
    def sendThrottled(self, nodeIndex):
        if self.jsonData != None:
            self.setDeviceFromMessage(nodeIndex, self.jsonData[nodeIndex], self.throttleData[nodeIndex], "sendThrottled")

    # Check if a throttle is active for a device index
    def isThrottleActive(self, nodeLastUpdate, nodeThrottle):
        return ((self.utcTime()) - nodeLastUpdate) < int(nodeThrottle)

    # Return UTC time
    def utcTime(self):
        return datetime.now(timezone.utc).timestamp()

    ##### MqttMapper initialization routine #####

    # Executed on plug-in start
    def onStart(self):
        # Parse options
        self.debugging = Parameters["Mode6"]
        self.dumpConfigToLog()
        if self.debugging == "Verbose+":
            Domoticz.Debugging(2+4+8+16+64+128)
        elif self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        elif self.debugging == "Debug":
            Domoticz.Debugging(2+4+8)
        elif self.debugging == "Normal":
            Domoticz.Debugging(2+4)

        self.mqttserveraddress = Parameters["Address"].replace(" ", "")
        self.mqttserverport = Parameters["Port"].replace(" ", "")

        # Load JSON mapping file
        jsonFile = Parameters['HomeFolder'] + Parameters["Mode1"]
        self.jsonData = None
        # Check for configuration file
        if not os.path.isfile(jsonFile):
            Domoticz.Error(F"Can't find {jsonFile} file!")
            return
        with open(jsonFile, encoding = 'UTF-8') as configStream:
            try:
                self.jsonData = json.load(configStream)
            except Exception as exception:
                Domoticz.Error(F"Error loading {jsonFile}: {str(exception)}")
                Domoticz.Error(F"You should probably use any online 'json format checker' to locate JSON syntax error in {jsonFile}")
                return

        # Go through JSON file to create devices
        deviceList = []
        for node in self.jsonData.items():
            nodeName = node[0]
            nodeItems = node[1]
            nodeTopic = self.getValue(nodeItems, 'topic', None)
            nodeKey = self.getValue(nodeItems, 'key', nodeTopic)
            nodeType = self.getValue(nodeItems, 'type', "0")
            nodeSubtype = self.getValue(nodeItems, 'subtype', "0")
            nodeSwitchtype = self.getValue(nodeItems, 'switchtype', "0")
            nodeOptions  = self.getValue(nodeItems, 'options', None)
            nodeVisible  = self.getValue(nodeItems, 'visible', True)

            if nodeName != None and nodeTopic != None and nodeType != None and nodeSubtype != None:
                # Create device if needed, update it if it already exists
                device = self.getDevice(nodeKey)
                if (nodeKey in deviceList):
                    Domoticz.Error(F"Duplicate {nodeKey} node/key - Please make them unique")
                else:
                    deviceList.append(nodeKey)
                if (device == None):
                    Domoticz.Log(F"Creating device {nodeName}")
                    Domoticz.Device(Name=nodeName, Unit=self.getNextDeviceId(), Type=int(nodeType), Subtype=int(nodeSubtype), Switchtype=int(nodeSwitchtype), DeviceID=nodeKey if nodeKey else nodeTopic, Options=nodeOptions, Used=nodeVisible).Create()
                    initialData = self.getValue(nodeItems, 'initial', None)
                    if initialData:                                 # Set initial data if required
                        nValue = int(self.getValue(initialData, 'nvalue', 0))
                        sValue = self.getValue(initialData, 'svalue', '')
                        Domoticz.Log(F"Initializing {nodeName} with nValue={nValue} and sValue={sValue}")
                        device = self.getDevice(nodeKey)
                        if device != None:
                            device.Update(nValue = nValue, sValue = sValue)
                        else:
                                    Domoticz.Error(F"Can't find device {nodeKey}")
                else:
                    # Update device only if something changed
                    if nodeOptions == None:
                        nodeOptions = {}
                    if device.Type != int(nodeType) or device.SubType != int(nodeSubtype) or device.SwitchType != int(nodeSwitchtype or device.Options != nodeOptions):
                        Domoticz.Log(F"Updating device {nodeName}")
                        device.Update(nValue = device.nValue, sValue = device.sValue, Type=int(nodeType), Subtype=int(nodeSubtype), Switchtype=int(nodeSwitchtype), Options=nodeOptions)

        # Connect to MQTT server
        self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
        parametersFile = Parameters['HomeFolder'] + Parameters["Mode1"] + ".parameters"
        try:
            with open(parametersFile, "wt") as f:
                fields = {}
                fields["mqttHost"] = self.mqttserveraddress
                fields["mqttPort"] = self.mqttserverport
                fields["mqttUsername"] = Parameters["Username"]
                fields["mqttPassword"] = Parameters["Password"]
                f.write(json.dumps(fields, indent=4))
                try:
                    os.chmod(parametersFile, 0o666)
                except Exception as exception:
                    Domoticz.Error(F"Error {str(exception)} changing {parametersFile} protection")
        except Exception as exception:
            Domoticz.Error(F"Error {str(exception)} opening {parametersFile}")
        self.initDone = True
        # Enable heartbeat
        self.lastHeartbeatUtc = self.utcTime()
        self.lastMqttCheckUtc = self.utcTime()
        Domoticz.Heartbeat(3)

    # Executed every "Domoticz.Heartbeat" interval seconds
    def onHeartbeat(self):
        # Exit if init not properly done
        if not self.initDone or self.mqttClient == None:
            return

        # Get UTC time
        nowUtc = self.utcTime()

        # Reconnect if connection has dropped every 15 seconds
        if (nowUtc - self.lastMqttCheckUtc) > 15:
            self.lastMqttCheckUtc = nowUtc
            if self.mqttClient.mqttConn == None or not self.mqttClient.isConnected:
                Domoticz.Debug(F"Reconnecting")
                self.mqttClient.Open()
        else:
            self.mqttClient.Ping()

        # Check if UTC time was set backward
        if nowUtc < self.lastHeartbeatUtc:
            Domoticz.Log(F"UTC time set backward, releasing all changes")
            # Scan all throttle date
            for nodeIndex in self.throttleLastDate:
                # Do we have a pending message?
                if self.throttleData[nodeIndex] != "":
                    # Send pending message (last date will be updated in setDeviceFromMessage)
                    self.sendThrottled(nodeIndex)
                else:
                    # Overwrite last date taking in account time already spent between last UTC and last message date
                    self.throttleLastDate[nodeIndex] = nowUtc - (self.lastHeartbeatUtc - self.throttleLastDate[nodeIndex])
        else:
            # Release all pending expired throttled messages
            for nodeIndex in self.throttleLastDate:
                # Do we have a pending message?
                if self.throttleData[nodeIndex] != "" and self.jsonData != None:
                    # Is throttle expired?
                    if not self.isThrottleActive(self.throttleLastDate[nodeIndex], self.getValue(self.jsonData[nodeIndex], 'throttle', 0)):
                        # Send pending message (last date will be updated in setDeviceFromMessage)
                        self.sendThrottled(nodeIndex)

        # Set last heartbeat time
        self.lastHeartbeatUtc = nowUtc

    ##### MQTT received message is used to change Domoticz's device state/data #####

    # Executed on MQTT publishing
    def onMQTTPublish(self, topic, rawmessage):
        # Exit if init not properly done
        if not self.initDone or self.jsonData == None:
            return

        if self.debugging == "Extra verbose":
            self.dumpMQTTMessageToLog(topic, rawmessage, 'onMQTTPublish: ')

        # Iterating through the JSON list
        for node in self.jsonData.items():
            nodeItems = node[1]
            nodeTopic = self.getValue(nodeItems, 'topic', None)     # Get MQTT topic
            if nodeTopic == topic:                                  # Is this the right topic?
                # Check for throttle value in node description
                nodeThrottle = self.getValue(nodeItems, 'throttle', None)
                if nodeThrottle != None:
                    # We have a throttle value, extract last message date
                    if node[0] in self.throttleLastDate:
                        # Is throttle active?
                        if self.isThrottleActive(self.throttleLastDate[node[0]], nodeThrottle):
                            self.throttleData[node[0]] = rawmessage
                            return
                    else:
                        # Save last message date (this first time we have amessage for this device)
                        self.throttleLastDate[node[0]] = self.utcTime()
                # No throttle or throttle not active, use message right now
                self.setDeviceFromMessage(node[0], nodeItems, rawmessage, "onMQTTPublish")

    # Set device value giving a message, either directly or throttled
    def setDeviceFromMessage(self, nodeIndex, nodeItems, rawmessage, source):
        # Delete throttled message and set last message date
        if nodeIndex in self.throttleLastDate:
            self.throttleLastDate[nodeIndex] = self.utcTime()
            self.throttleData[nodeIndex] = ""
        # Try to decode JSON message
        message = ""
        try:
            message = json.loads(rawmessage.decode('utf8'))
        except ValueError:
            message = rawmessage.decode('utf8')
        except Exception as e:
            errorLine = 0
            if e.__traceback__ != None:
                errorLine = e.__traceback__.tb_lineno
            Domoticz.Error(F"Error decoding {rawmessage} - {type(e).__name__} at line {errorLine} of {__file__}: {e}")
        nodeTopic = self.getValue(nodeItems, 'topic', None)         # Get MQTT topic
        nodeKey = self.getValue(nodeItems, 'key', nodeTopic)        # Get device key
        device = self.getDevice(nodeKey)
        if device == None:
            Domoticz.Error(F"Can't find device key {nodeKey}")
            return
        Domoticz.Debug(source+" found "+str(nodeTopic)+", Device '" + device.Name + "', message '" + str(message) + "'")
        nodeSelect = self.getValue(nodeItems, 'select', None)       # Is there a "select" option?
        nodeReject = self.getValue(nodeItems, 'reject', None)       # Is there a "reject" option?
        # Do we have a "select" option?
        topicSelected = True                                        # By default, accept message
        if nodeSelect != None:
            if type(nodeSelect).__name__ == "list":
                # This is a list, scan it
                for nodeSelectItem in nodeSelect:
                    if not self.itemFoundInMessage(nodeSelectItem, message, nodeKey):
                        topicSelected = False
            elif type(nodeSelect).__name__ == "dict":
                # This is a dict, use it
                if not self.itemFoundInMessage(nodeSelect, message, nodeKey):
                    topicSelected = False
            else:
                # What's that?
                Domoticz.Error(F"Can't understand 'select' with type {type(nodeSelect).__name__} for nodeKey")
                topicSelected = False
        # Do we have a "reject" option?
        if nodeReject != None:
            if type(nodeReject).__name__ == "list":
                # This is a list, scan it
                for nodeRejectItem in nodeReject:
                    if not self.itemNotFoundInMessage(nodeRejectItem, message, nodeKey):
                        topicSelected = False
            elif type(nodeReject).__name__ == "dict":
                # This is a dict, use it
                if not self.itemNotFoundInMessage(nodeReject, message, nodeKey):
                    topicSelected = False
            else:
                # What's that?
                Domoticz.Error(F"Can't understand 'reject' with type {type(nodeReject).__name__} for nodeKey")
                topicSelected = False
        if topicSelected:
            nodeType = self.getValue(nodeItems, 'type', "0")        # Read some values for this device
            nodeSubtype = self.getValue(nodeItems, 'subtype', "0")
            nodeSwitchtype = self.getValue(nodeItems, 'switchtype', "0")
            nodeMapping = self.getValue(nodeItems, 'mapping', None)
            mappingItem = self.getValue(nodeMapping, 'item', None)
            mappingDefault = self.getValue(nodeMapping, 'default', None)
            mappingValues = self.getValue(nodeMapping, 'values', None)
            mappingBattery = self.getValue(nodeMapping, 'battery', None)
            valueToSet = None
            if mappingItem !=None:
                if mappingItem == '':                               # Empty mapping means (not json) full message
                    mappingItem = "~*"
                readValue = ''
                itemIndex = -1
                isOnlyMessage = None
                items = mappingItem.split(';')                      # Work with multiple items values
                for item in items:                                  # Read all values to map
                    readValue += ";"                                # Add ';' as separator
                    itemIndex += 1                                  # Increment index
                    if item[0:1] == '~':                            # Does item start with '~'?
                        if item == '~':                             # If item is just '~', insert previous sValue item
                            sValue = device.sValue.split(';')       # Extract current sValue
                            if itemIndex < len(sValue):             # Is index within device sValue range?
                                valueToSet = sValue[itemIndex]      # Yes, load it
                            else:
                                valueToSet = ''                     # No, use empty string
                            readValue += str(valueToSet)            # Insert the value
                            isOnlyMessage = False
                        elif item == "~*":                          # Item is ~*, insert topic content
                            readValue += str(self.computeValue(message, nodeMapping, itemIndex))
                            if isOnlyMessage == None:
                                    isOnlyMessage = True
                        else:
                            isOnlyMessage = False
                            readValue += item[1:]                   # Add item, removing initial '~'
                    else:
                        isOnlyMessage = False
                        itemValue = self.getPathValue(message, item, '/', None) # Extract value from message
                        if itemValue == None:
                            Domoticz.Error(F"Can't find >{item}'< in >'{message}<, message ignored")
                            return
                        else:                                       # Add extracted value
                            readValue += str(self.computeValue(itemValue, nodeMapping, itemIndex))
                readValue = readValue[1:]                           # Remove first ';'
                if  mappingValues != None:
                    valueToSet = mappingDefault or 0                # Set default mapping (or 0)
                    for testValue in mappingValues:                 # Scan all mapping values
                        Domoticz.Log(F'testValue="{testValue}" ({type(testValue).__name__}), readValue="{readValue}" ({type(readValue).__name__})')
                        if type(testValue).__name__ == "bool":
                            if testValue == self.convertToBool(readValue):
                                valueToSet = mappingValues[testValue]   # Insert mapped value
                        else:
                            if str(testValue) == str(readValue):    # Is this the same value?
                                valueToSet = mappingValues[testValue]   # Insert mapped value
                else:
                    if isOnlyMessage == True:                       # If we have only message into readValue
                        valueToSet = rawmessage.decode('utf8')      # Use original message instead of it's dict representation
                    else:                                           # Read value is more complex
                        valueToSet = readValue                      # Set value = read value
            else:                                                   # No mapping given
                Domoticz.Error(F"No mapping for {device.Name}")

            if valueToSet != None:                                  # Value given, set it
                batteryValue = 255
                if mappingBattery != None:
                    batteryValue = self.getPathValue(message, mappingBattery, '/', 255) # Extract battery value from message
                if batteryValue < 0:
                    batteryValue = 0
                elif batteryValue > 100 and batteryValue != 255:
                    batteryValue = 100
                if batteryValue != 255:
                    batteryText = F", batteryLevel: {batteryValue}"
                else:
                    batteryText =""
                if self.isFloat(valueToSet):                        # Set nValue and sValue depending on value type (numeric or not, switch or not)
                    readValue = str(valueToSet)                     # Force read value as string
                    if self.switchTypes.isSwitch(nodeType):         # This is a switch
                        if self.switchTypes.isLevelSwitch(nodeType, nodeSubtype, nodeSwitchtype): # This is a switch with dimmer or level
                            nValueToSet = 0 if str(valueToSet) == '0' else 1 if str(valueToSet) == '100' else 2
                            sValueToSet = str(valueToSet)
                        else:                                       # Not a dimmer/level switch
                            nValueToSet = 0 if str(valueToSet) == '0' else 1
                            sValueToSet = ""
                    else:
                        if self.switchTypes.hasNvalueData:          # If device has nValue data, round sValue (text)
                            nValueToSet = int(round(float(valueToSet),0))
                        else:
                            # Set nValue to zero
                            nValueToSet = 0
                        sValueToSet = readValue
                    Domoticz.Log(F"Setting {device.Name} to {nValueToSet}/{sValueToSet}{batteryText}")  # Value is numeric or float
                    device.Update(nValue=nValueToSet, sValue=sValueToSet, BatteryLevel=batteryValue)
                else:                                               # Value is not numeric
                    Domoticz.Log(F"Setting {device.Name} to >{valueToSet}<{batteryText}")
                    device.Update(nValue=0, sValue=str(valueToSet), BatteryLevel=batteryValue)

    ##### Domoticz's device state/data change is sent to MQTT #####

    # Executed when Domoticz (on user request) send a command
    def onCommand(self, Unit, Command, Level, sColor):
        # Exit if init not properly done
        if not self.initDone:
            return
        # Get device
        device = Devices[Unit]
        Domoticz.Log(F"{device.DeviceID}: Command: '{Command}', Level: {Level}, Color: {sColor}")
        # Get define JSON definition
        nodeItems = self.getDeviceDefinition(device)
        # Load supported commands
        nodeCommands = self.getValue(nodeItems, 'commands', None)
        # Any defined command?
        if nodeCommands != None:
            # Locate command into list (save default some found)
            defaultCommand = None
            thisCommand = None
            # Scan all commands for this device
            for nodeCommand in nodeCommands.keys():
                if nodeCommand.lower() == Command.lower():
                    # This is the same command
                    thisCommand = nodeCommands[nodeCommand]
                elif nodeCommand.lower() == "<default>":
                    # Save default value if found
                    defaultCommand = nodeCommands[nodeCommand]
            # Load default if command not found
            if thisCommand == None:
                thisCommand = defaultCommand
            # Did we got a command definition?
            if thisCommand != None:
                # Try loading topic
                commandTopic = self.getValue(thisCommand, 'topic', None)
                if commandTopic != None:
                    # Topic found, load payload and retain
                    commandPayload = self.getValue(thisCommand, 'payload', "")
                    commandRetain = self.getValue(thisCommand, 'retain', False)
                    if type(commandPayload).__name__ == "str":
                        if commandPayload.startswith('"') and commandPayload.endswith('"'):
                            payload = commandPayload[1:-1]
                        else:
                           payload = commandPayload
                    else:
                        payload = json.dumps(commandPayload)
                    payload = payload.replace("<command>", str(Command)).replace("<level>", str(Level)).replace("<color>", str(sColor))
                    Domoticz.Log(F"Setting {commandTopic} to >{payload}<, retain={commandRetain}")
                    if self.mqttClient != None:
                        self.mqttClient.Publish(commandTopic, payload, 1 if commandRetain else 0)
                else:
                    commandCommand = self.getValue(thisCommand, 'command', None)
                    if commandCommand != None:
                        # Command found, execute it
                        commandCommand = str(commandCommand).replace("<command>", str(Command)).replace("<level>", str(Level)).replace("<color>", str(sColor))
                        self.executeCommand(commandCommand)
                    else:
                        Domoticz.Error(F"Can't find 'topic' nor 'command' in {thisCommand}. Please fix it!")
            else:
                    Domoticz.Error(F"Can't find command {Command} nor <default> in {nodeCommands}")

        else:
            # No defined commands, use default settings for on/off/set level
            targetValue = None
            if Command == 'Off':
                targetValue = '0'
            elif Command == 'On':
                targetValue = '100'
            elif Command == 'Set Level':
                targetValue = str(Level)
            elif self.isFloat(Command):                             # If command is numeric or float
                targetValue = Command
            else:
                Domoticz.Error(F'Command: "{Command}" not supported by default. Please add "commands" for {device.Name}')
            # Try to set value
            self.setTargetValue (targetValue, device)

    # Sends a SET message
    def setTargetValue(self, targetValue, device):
        if targetValue != None and self.jsonData != None and self.mqttClient != None: # Only if a target value has been given, and jsonData loaded
            nodeItems = self.getDeviceDefinition(device)
            nodeMapping = self.getValue(nodeItems, 'mapping', None)
            nodeSet = self.getValue(nodeItems, 'set', None)
            setTopic = None
            setPayload = None
            valueToSet = None
            if nodeSet != None:                                     # Do we have some SET parameters?
                localCommand = self.getValue(nodeSet, 'command', None)      # Get command, default to None
                nodeTopic = self.getValue(nodeItems, 'topic', None) # Get MQTT topic
                setTopic = self.getValue(nodeSet, 'topic', None if localCommand else nodeTopic) # Get topic, default to None if a command has been given, subscribed topic else
                setPayload = self.getValue(nodeSet, 'payload', "#") # Get value, default to #
                setRetain = self.getValue(nodeSet, 'retain', True)  # Get retain, default to true
                setMapping = self.getValue(nodeSet, 'mapping', None)# Get set mapping, default to None
                setMappingValues = self.getValue(setMapping, 'values', None)# Get set mapping values, default to None
                mappingValues = self.getValue(nodeMapping, 'values', None)  # Get mapping values, default to None
                nodeType = self.getValue(nodeItems, 'type', "0")
                nodeSubtype = self.getValue(nodeItems, 'subtype', "0")
                nodeSwitchtype = self.getValue(nodeItems, 'switchtype', "0")
                if self.switchTypes.canBeSet(nodeType, nodeSubtype, nodeSwitchtype): # Select valid types
                    if setMappingValues != None:
                        for testValue in setMappingValues:          # Scan all mapping values
                            if setMappingValues[testValue] == targetValue:  # Is this the same value?
                                valueToSet = testValue              # Insert mapped value
                        if valueToSet == None:                      # No mapping value found
                            Domoticz.Error(F"Can't map >{targetValue}< for {device.Name}")
                    elif mappingValues != None:
                        for testValue in mappingValues:             # Scan all mapping values
                            if mappingValues[testValue] == targetValue:  # Is this the same value?
                                valueToSet = testValue              # Insert mapped value
                        if valueToSet == None:                      # No mapping value found
                            Domoticz.Error(F"Can't map >{targetValue}< for {device.Name}")
                    else:                                           # No mapping given, use command value
                        valueToSet = str(self.computeValue(targetValue, nodeMapping, 0, nodeSet))
                else:                                               # Device not in canBeSet list
                    Domoticz.Error(F"Can't set device type {nodeType}, subtype {nodeSubtype}, switchtype {nodeSwitchtype} yet. Please ask for support.")
                    return
                if valueToSet != None and setTopic != None:         # Value and topic given, set it
                    if isinstance(setPayload, str):
                        payload = str(setPayload).replace("#", valueToSet)  # payload is a simple string
                    else:
                        payload = json.dumps(setPayload).replace("#", valueToSet)   # payload is a JSON dictionay
                    Domoticz.Log(F"Setting {setTopic} to >{payload}<, retain={setRetain}")
                    self.mqttClient.Publish(setTopic, payload, 1 if setRetain else 0)
                if localCommand != None:                            # Command given, execute it
                    localCommand = str(localCommand).replace("#", str(valueToSet)) # Replace "#" in command by value
                    self.executeCommand(localCommand)
            else:                                                   # No set given
                Domoticz.Error(F"No SET parameters for {device.Name}/{device.DeviceID} in {nodeItems}")

#   --------------------------------------------
#   --------------- Plug-in code ---------------
#   --------------------------------------------

# Declare plug-in class instance
global _plugin
_plugin = BasePlugin()

# Forward all events to plug-in class
def onStart():
    global _plugin
    _plugin.onStart()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onDeviceAdded(Unit):
    global _plugin
    _plugin.onDeviceAdded(Unit)

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

def onDeviceRemoved(Unit):
    global _plugin
    _plugin.onDeviceRemoved(Unit)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()