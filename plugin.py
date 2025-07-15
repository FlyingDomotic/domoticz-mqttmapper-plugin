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
<plugin key="MqttMapper" name="MQTT mapper with network interface" author="Flying Domotic" version="25.7.7-1" externallink="https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin">
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
import os
import json
from typing import Any

# Used by VsCodium when running outside Domoticz environment
#   to simulate internal Domoticz functions/variables definition
try:
    from Domoticz import *
except:
    pass

#   ----------------------------------------------
#   --------------- Local routines ---------------
#   ----------------------------------------------

# Extract a version number in format 1.2.3-4
def extractVersion(version: str) -> list:
    result = []
    part = ""
    for char in version:
        if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            part += char
        else:
            if part != "":
                result.append(part)
                part = ""
    if part != "":
        result.append(part)
    return result

# Compare 2 versions in format 1.2.3-4
def compareVersions(version1: str, version2: str) -> int:
    version1Parts = extractVersion(version1)                        # Exxtract versions
    version2Parts = extractVersion(version2)
    for i in range(min(len(version1Parts), len(version2Parts))):    # Compare common part
        if int(version1Parts[i]) > int(version2Parts[i]):           # This par is greater in version1
            return 1
        elif int(version1Parts[i]) < int(version2Parts[i]):         # This part is lower in version 1
            return -1
        # Here, parts are thr same
    if len(version1) > len(version2):                               # Verions1 has more items than version2
        return 1
    elif len(version1) < len(version2):                             # Verions1 has less items than version2
        return -1
    # Here parts are the same and have same length
    return 0

# Returns a dictionary value giving a key or default value if not existing
def getValue(searchDict, searchKey, defaultValue: Any =''):
    if searchDict == None:
        return defaultValue
    else:
        if searchKey in searchDict:
            if searchDict[searchKey] == None:
                return defaultValue
            else:
                return searchDict[searchKey]
        else:
            return defaultValue

#   --------------------------------------------
#   --------------- Plug-in code ---------------
#   --------------------------------------------

# Declare plug-in class instance
global _plugin
_plugin = None

# Forward all events to plug-in class
def onStart():
    global _plugin

    # Parse options
    debugging = Parameters["Mode6"]
    if debugging == "Verbose+":
        Domoticz.Debugging(2+4+8+16+64+128)
    elif debugging == "Verbose":
        Domoticz.Debugging(2+4+8+16+64)
    elif debugging == "Debug":
        Domoticz.Debugging(2+4+8)
    elif debugging == "Normal":
        Domoticz.Debugging(2+4)

    # Load JSON mapping file
    jsonFile = Parameters['HomeFolder'] + Parameters["Mode1"]
    jsonData = None
    # Check for configuration file
    if not os.path.isfile(jsonFile):
        Domoticz.Error(F"Can't find {jsonFile} file!")
        return
    with open(jsonFile, encoding = 'UTF-8') as configStream:
        try:
            jsonData = json.load(configStream)
        except Exception as exception:
            Domoticz.Error(F"Error loading {jsonFile}: {str(exception)}")
            Domoticz.Error(F"You should probably use any online 'json format checker' to locate JSON syntax error in {jsonFile}")
            return

    parameters = getValue(jsonData, "[parameters]", None)
    fileFormat = getValue(parameters, "version", "1.0")
    Domoticz.Log(F"{jsonFile} is a version {fileFormat} file")
    if fileFormat < "2.0":
        from pluginV1 import pluginV1
        _plugin = pluginV1(Parameters, Devices)
    #elif fileFormat == "2.0":
    #    from pluginV2 import pluginV2
    #    _plugin = pluginV2()
    else:
        Domoticz.Error(F"Unknown file version {fileFormat}!")
        return
    _plugin.onStart()

def onConnect(Connection, Status, Description):
    global _plugin
    if _plugin != None:
        _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    if _plugin != None:
        _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    if _plugin != None:
        _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    if _plugin != None:
        _plugin.onCommand(Unit, Command, Level, Color)

def onDeviceAdded(Unit):
    global _plugin
    if _plugin != None:
        _plugin.onDeviceAdded(Unit)

def onDeviceModified(Unit):
    global _plugin
    if _plugin != None:
        _plugin.onDeviceModified(Unit)

def onDeviceRemoved(Unit):
    global _plugin
    if _plugin != None:
        _plugin.onDeviceRemoved(Unit)

def onHeartbeat():
    global _plugin
    if _plugin != None:
        _plugin.onHeartbeat()