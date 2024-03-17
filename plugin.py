# MqttMapper is a Domoticz Python plug in allowing to map MQTT topics directly to Domoticz devices.
#
#   If you want to be able to read/write some MQTT topics and maps them to Domoticz devices, without having to install NodeRed,
#       and/pr integrate sensors that don't have HomeAssistant discovery item, this plug-in is made for you.
#
# MqttMapper est un plugin Domoticz qui permet de relier des dispositifs Domoticz à MQTT directement.
#
#   Si vous voulez lire/écrire des topics MQTT et les lier à des dispositifs Domoticz, sans avoir besoin d'installer NodeRed,
#       et/ou intégrer des capteurs qui n'ont pas de découvertes HomeAssistant, ce plug-in est fait pour vous.
#
#   Flying Domotic - https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin
"""
<plugin key="MqttMapper" name="MQTT mapper with LAN interface" author="Flying Domotic" version="1.0.25" externallink="https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin">
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
import Domoticz
from datetime import datetime
from itertools import count, filterfalse
import json
import time
import traceback

class MqttClient:
    Address = ""
    Port = ""
    mqttConn = None
    mqttConnectedCb = None
    mqttDisconnectedCb = None
    mqttPublishCb = None

    def __init__(self, destination, port, mqttConnectedCb, mqttDisconnectedCb, mqttPublishCb, mqttSubackCb):
        Domoticz.Debug("MqttClient::__init__")
        self.Address = destination
        self.Port = port
        self.mqttConnectedCb = mqttConnectedCb
        self.mqttDisconnectedCb = mqttDisconnectedCb
        self.mqttPublishCb = mqttPublishCb
        self.mqttSubackCb = mqttSubackCb
        self.Open()

    def __str__(self):
        Domoticz.Debug("MqttClient::__str__")
        if (self.mqttConn != None):
            return str(self.mqttConn)
        else:
            return "None"

    def Open(self):
        Domoticz.Debug("MqttClient::Open")
        if (self.mqttConn != None):
            self.Close()
        self.isConnected = False
        self.mqttConn = Domoticz.Connection(Name=self.Address, Transport="TCP/IP", Protocol="MQTT", Address=self.Address, Port=self.Port)
        self.mqttConn.Connect()

    def Connect(self):
        Domoticz.Debug("MqttClient::Connect")
        if (self.mqttConn == None):
            self.Open()
        else:
            ID = 'Domoticz_'+Parameters['Key']+'_'+str(Parameters['HardwareID'])+'_'+str(int(time.time()))
            Domoticz.Log("MQTT CONNECT ID: '" + ID + "'")
            self.mqttConn.Send({'Verb': 'CONNECT', 'ID': ID})

    def Ping(self):
        #Domoticz.Debug("MqttClient::Ping")
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'PING'})

    def Publish(self, topic, payload, retain = 0):
        Domoticz.Debug("MqttClient::Publish " + topic + " (" + payload + ")")
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'PUBLISH', 'Topic': topic, 'Payload': bytearray(payload, 'utf-8'), 'Retain': retain})

    def Subscribe(self, topics):
        Domoticz.Debug("MqttClient::Subscribe")
        subscriptionlist = []
        for topic in topics:
            subscriptionlist.append({'Topic':topic, 'QoS':0})
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'SUBSCRIBE', 'Topics': subscriptionlist})

    def Close(self):
        Domoticz.Log("MqttClient::Close")
        #TODO: Disconnect from server
        self.mqttConn = None
        self.isConnected = False

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("MqttClient::onConnect")
        if (Status == 0):
            Domoticz.Log("Successful connect to: "+Connection.Address+":"+Connection.Port)
            self.Connect()
        else:
            Domoticz.Error("Failed to connect to: "+Connection.Address+":"+Connection.Port+", Description: "+Description)

    def onDisconnect(self, Connection):
        Domoticz.Log("MqttClient::onDisonnect Disconnected from: "+Connection.Address+":"+Connection.Port)
        self.Close()
        # TODO: Reconnect?
        if self.mqttDisconnectedCb != None:
            self.mqttDisconnectedCb()

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

class BasePlugin:
    # MQTT settings
    mqttClient = None
    mqttserveraddress = ""
    mqttserverport = ""
    debugging = "Normal"
    jsonData = None
    initDone = False

    # Returns a dictionary value giving a key or default value if not existing
    def getValue(self, dict, key, default=''):
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

    # Return a path in a dictionary or default value if not existing
    def getPathValue (self, dict, path, separator = '/', default=''):
        pathElements = path.split(separator)
        element = dict
        try:
            for pathElement in pathElements:
                if pathElement not in element:
                    return default
                element = element[pathElement]
        except TypeError as te:
            element = default
        return element

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

    def deviceStr(self, unit):
        name = "<UNKNOWN>"
        if unit in Devices:
            name = Devices[unit].Name
        return format(unit, '03d') + "/" + name

    def getUnit(self, device):
        unit = -1
        for k, dev in Devices.items():
            if dev == device:
                unit = k
        return unit

    def onStart(self):
        # Parse options
        self.debugging = Parameters["Mode6"]
        DumpConfigToLog()
        if self.debugging == "Extra verbose":
            Domoticz.Debugging(2+4+8+16+64)
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
        with open(jsonFile, encoding = 'UTF-8') as configStream:
            try:
                self.jsonData = json.load(configStream)
            except:
                Domoticz.Error("Error reading JSON file "+jsonFile)
                return
        # Go through Json file to create devices
        for node in self.jsonData.items():
            nodeName = node[0]
            nodeItems = node[1]
            nodeTopic = self.getValue(nodeItems, 'topic', None)
            nodeKey = self.getValue(nodeItems, 'key', None)
            nodeType = self.getValue(nodeItems, 'type', None)
            nodeSubtype = self.getValue(nodeItems, 'subtype', None)
            nodeSwitchtype = self.getValue(nodeItems, 'switchtype', "0")
            nodeOptions  = self.getValue(nodeItems, 'options', None)

            if nodeName != None and nodeTopic != None and nodeType != None and nodeSubtype != None:
                # Create device if needed, update it if it already exists
                device = self.getDevice(nodeKey if nodeKey else nodeTopic)
                if (device == None):
                    Domoticz.Log("Creating device " + nodeName)
                    Domoticz.Device(Name=nodeName, Unit=self.getNextDeviceId(), Type=int(nodeType), Subtype=int(nodeSubtype), Switchtype=int(nodeSwitchtype), DeviceID=nodeKey if nodeKey else nodeTopic, Options=nodeOptions, Used=True).Create()
                    initialData = self.getValue(nodeItems, 'initial', None)
                    if initialData: # Set initial data if required
                        nValue = int(self.getValue(initialData, 'nvalue', 0))
                        sValue = self.getValue(initialData, 'svalue', '')
                        Domoticz.Log(f"Initializing {nodeName} with nValue={nValue} and sValue={sValue}")
                        device = self.getDevice(nodeKey if nodeKey else nodeTopic)
                        device.Update(nValue = nValue, sValue = sValue)
                else:
                    Domoticz.Log("Updating device " + nodeName)
                    device.Update(nValue = device.nValue, sValue = device.sValue, Type=int(nodeType), Subtype=int(nodeSubtype), Switchtype=int(nodeSwitchtype), Options=nodeOptions)

        # Connect to MQTT server
        self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)

        self.initDone = True
        # Enable heartbeat
        Domoticz.Heartbeat(60)

    def onConnect(self, Connection, Status, Description):
        # Exit if init not properly done
        if not self.initDone:
            return
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        # Exit if init not properly done
        if not self.initDone:
            return
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        # Exit if init not properly done
        if not self.initDone:
            return
        self.mqttClient.onMessage(Connection, Data)

    def onMQTTConnected(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Debug("onMQTTConnected")
        self.mqttClient.Subscribe(self.getTopics())

    def onMQTTDisconnected(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTPublish(self, topic, rawmessage):
        # Exit if init not properly done
        if not self.initDone:
            return
        message = ""
        try:
            message = json.loads(rawmessage.decode('utf8'))
        except ValueError:
            message = rawmessage.decode('utf8')

        topiclist = topic.split('/')
        if self.debugging == "Extra verbose":
            DumpMQTTMessageToLog(topic, rawmessage, 'onMQTTPublish: ')

        # Iterating through the JSON list
        for node in self.jsonData.items():
            nodeItems = node[1]
            nodeTopic = self.getValue(nodeItems, 'topic', None) # Get MQTT topic
            nodeKey = self.getValue(nodeItems, 'key', None) # Get device key
            if nodeTopic == topic:  # Is this the right topic?
                device = self.getDevice(nodeKey if nodeKey else nodeTopic)
                Domoticz.Debug("onMQTTConnected found "+str(topic)+", Device '" + device.Name + "'")
                nodeType = self.getValue(nodeItems, 'type', None)   # Read some values for this device
                nodeSubtype = self.getValue(nodeItems, 'subtype', None)
                nodeSwitchtype = self.getValue(nodeItems, 'switchtype', "0")
                nodeMapping = self.getValue(nodeItems, 'mapping', None)
                mappingItem = self.getValue(nodeMapping, 'item', None)
                mappingDefault = self.getValue(nodeMapping, 'default', None)
                mappingValues = self.getValue(nodeMapping, 'values', None)
                valueToSet = None
                if mappingItem !=None:
                    if mappingItem == '':   # Empty mapping means (not json) full message
                        readValue = str(message)
                    else:   # We have a mapping item
                        readValue = ''
                        itemIndex = -1
                        items = mappingItem.split(';')  # Work with multiple items values
                        for item in items:  # Read all values to map
                            readValue += ";"# Add ';' as separator
                            itemIndex += 1  # Increment index
                            if item[0:1] == '~': # Does item start with '~'?
                                if item == '~': # If item is just '~', insert previous sValue item
                                    sValue = device.sValue.split(';')   # Extract current sValue
                                    if itemIndex < len(sValue): # Is index within device sValue range?
                                        valueToSet = sValue[itemIndex]  # Yes, load it
                                    else:
                                        valueToSet = '' # No, use empty string
                                    readValue += str(valueToSet)    # Insert the value
                                elif item == "~*":  # Item is ~*, insert topic content
                                    if str(message).replace('.', '', 1).isdigit():  # If raw value is numeric or float
                                        multiplier = self.getValue(nodeMapping, 'multiplier', None) # Extract multiplier
                                        if multiplier !=None:   # Do we have a multiplier?
                                            readValue += str(float(str(message)) * float(multiplier)) # Yes, apply it
                                        else:
                                            readValue += str(message)   # Add full content
                                    else:
                                        readValue += str(message)   # Add full content
                                else:
                                    readValue += item[1:]   # Add item, removing initial '~'
                            else:
                                itemValue = self.getPathValue(message, item, '/', None) # Extract value from message
                                if itemValue == None:
                                    Domoticz.Error('Can\'t find >'+str(item)+'< in >'+str(message)+'<')
                                else:   # Add extracted value
                                    if str(itemValue).replace('.', '', 1).isdigit():  # If extracted value is numeric or float
                                        multiplier = self.getValue(nodeMapping, 'multiplier', None) # Extract multiplier
                                        if multiplier !=None:   # Do we have a multiplier?
                                            itemValue = float(itemValue) * float(multiplier) # Yes, apply it
                                    readValue += str(itemValue)
                        readValue = readValue[1:]   # Remove first ';'
                    if nodeType == '244':   # This is a switch
                        if  mappingDefault != None and mappingValues != None:
                            valueToSet = mappingDefault # Set default mapping
                            for testValue in mappingValues: # Scan all mapping values
                                Domoticz.Log(f'testValue="{testValue}" ({type(testValue)}), readValue="{readValue}" ({type(readValue)})')
                                if testValue == readValue:  # Is this the same value?
                                    valueToSet = mappingValues[testValue]   # Insert mapped value
                        else:
                            valueToSet = readValue  # Set value = read value
                    else:   # Not a switch
                        valueToSet = readValue
                else:   # No mapping given
                    Domoticz.Error('No mapping for '+device.Name)
                if valueToSet != None: # Value given, set it
                    if valueToSet.isnumeric():  # Set nValue and sValue depending on value type (numeric or not, switch or not)
                        multiplier = self.getValue(nodeMapping, 'multiplier', None)
                        if multiplier !=None:   # Do we have a multiplier?
                            valueToSet = float(valueToSet) * float(multiplier) # Yes, apply it
                            readValue = str(valueToSet) # Force value to set to float value (valueToSet will be truncated as integer later on)
                        if nodeType == '244':   # This is a switch
                            if nodeSwitchtype == '0': # This is an On/Off switch
                                nValueToSet = 0 if str(valueToSet) == '0' else 1
                            else:   # Not a switch, use given value
                                nValueToSet = int(valueToSet)
                            sValueToSet = str(valueToSet)
                        else:
                            nValueToSet = int(valueToSet)
                            sValueToSet = readValue
                        Domoticz.Log('Setting '+device.Name+' to '+str(nValueToSet)+'/'+sValueToSet)  # Value is numeric
                        device.Update(nValue=nValueToSet, sValue=sValueToSet)
                    else:   # Value is not numeric
                        Domoticz.Log('Setting '+device.Name+' to >'+valueToSet+'<') 
                        device.Update(nValue=0, sValue=str(valueToSet))

    def onMQTTSubscribed(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        # (Re)subscribed, refresh device info
        Domoticz.Debug("onMQTTSubscribed")
        topics = set()

# ==========================================================DASHBOARD COMMAND=============================================================
    def onCommand(self, Unit, Command, Level, sColor):
        # Exit if init not properly done
        if not self.initDone:
            return
        device = Devices[Unit]
        Domoticz.Log(self.deviceStr(Unit) + ", "+device.DeviceID+": Command: '" + str(Command) + "', Level: " + str(Level) + ", Color:" + str(sColor))
        targetValue = None
        if Command == 'Off':
            targetValue = '0'
        elif Command == 'On':
            targetValue = '100'
        elif Command == 'Set Level':
            targetValue = str(Level)
        else:
            Domoticz.Error('Command: "' + str(Command) + '" not supported yet for ' + device.Name+'. Please ask for support.')

        if targetValue != None: # Only if a target value has been given
            # Iterating through the JSON list
            for node in self.jsonData.items():
                nodeItems = node[1]
                nodeTopic = self.getValue(nodeItems, 'topic', None) # Get MQTT topic
                valueToSet = None
                if nodeTopic == device.DeviceID:  # Is this the right topic?
                    nodeMapping = self.getValue(nodeItems, 'mapping', None)
                    nodeSet = self.getValue(nodeItems, 'set', None)
                    if nodeSet !=None:  # Do we have some SET parameters?
                        setTopic = self.getValue(nodeSet, 'topic', nodeTopic)   # Get topic, default to subscribed topic
                        setPayload = self.getValue(nodeSet, 'payload', "#")     # Get value, default to #
                        mappingValues = self.getValue(nodeMapping, 'values', None)
                        nodeType = self.getValue(nodeItems, 'type', None)
                        if nodeType == '244' or  nodeType == '242' :   # This is a switch or a set temp device
                            if mappingValues != None:
                                for testValue in mappingValues: # Scan all mapping values
                                    if mappingValues[testValue] == targetValue:  # Is this the same value?
                                        valueToSet = testValue  # Insert mapped value
                                if valueToSet == None:  # No mapping value found
                                    Domoticz.Error('Can\'t map >'+targetValue+'< for '+device.Name)
                            else: # No mapping given, use command value
                                valueToSet = targetValue
                        else:   # Not a switch
                            Domoticz.Error('Can\'t set device type '+nodeType+' yet. Please ask for support.')
                    else:   # No set given
                        Domoticz.Error('No SET parameters for '+device.Name)
                    if valueToSet != None: # Value given, set it
                        if isinstance(setPayload, str):
                            payload = str(setPayload).replace("#", valueToSet)  # payload is a simple string
                        else:
                            payload = json.dumps(setPayload).replace("#", valueToSet)   # payload is a JSON dictionay
                        Domoticz.Log('Setting '+device.DeviceID+' to >'+payload+'<')
                        self.mqttClient.Publish(setTopic, payload, 1)

    def onDeviceAdded(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Log("onDeviceAdded " + self.deviceStr(Unit))

    def onDeviceModified(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        device = Devices[Unit]
        Domoticz.Log("onDeviceModified " + self.deviceStr(Unit) + ", " + device.DeviceID + ", sValue=" + device.sValue)

    def onDeviceRemoved(self, Unit):
        # Exit if init not properly done
        if not self.initDone:
            return
        Domoticz.Log("onDeviceRemoved " + self.deviceStr(Unit))

    def onHeartbeat(self):
        # Exit if init not properly done
        if not self.initDone:
            return
        if self.debugging == "Extra verbose":
            Domoticz.Debug("Heartbeating...")

        # Reconnect if connection has dropped
        if self.mqttClient.mqttConn is None or (not self.mqttClient.mqttConn.Connecting() and not self.mqttClient.mqttConn.Connected() or not self.mqttClient.isConnected):
            Domoticz.Debug("Reconnecting")
            self.mqttClient.Open()
        else:
            self.mqttClient.Ping()

    # Returns list of topics to subscribe to
    def getTopics(self):
        topics = set()
        # Go through Json file to extract topics
        for node in self.jsonData.items():
            nodeName = node[0]
            nodeItems = node[1]
            nodeTopic = self.getValue(nodeItems, 'topic', None)
            # Add topic if not already in list (as multiple devices on the same topic are allowed)
            if nodeTopic not in topics:
                topics.add(nodeTopic)
        Domoticz.Debug("getTopics: '" + str(topics) +"'")
        return list(topics)

global _plugin
_plugin = BasePlugin()

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

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Log( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Log("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Log("Device: " + str(x) + " - " + str(Devices[x]))

def DumpMQTTMessageToLog(topic, rawmessage, prefix=''):
    message = rawmessage.decode('utf8','replace')
    message = str(message.encode('unicode_escape'))
    Domoticz.Log(prefix+topic+":"+message)
