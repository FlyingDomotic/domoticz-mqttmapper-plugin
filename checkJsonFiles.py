#!/usr/bin/python3
#
#   Parse MqttMapper configuration file
#
#   This script analyzes all MqttMapper configuration files in its home folder
#
#   It checks for:
#       - JSON syntax,
#       - JSON items (all items should be known, with all mandatory items present),
#       - Item type (integer, floating number, string, list...) are also checked,
#       - Type, sub type and switch type should be known and their association supported,
#       - Initial/svalue present when device has multiple sValue items,
#       - Initial, multiplier and digits values for devices with multiple sValue items,
#       - Digit count for devices with floating point sValue item(s),
#       - Duplicate Domoticz device names.
#
#   Author: Flying Domotic
#   License: GPL 3.0

codeVersion = "25.6.24-1"

import glob
import os
import pathlib
import getopt
import sys
import json
from datetime import datetime
from typing import Any
from FF_checkV1File import FF_checkV1File

# Print a message to screen and output stream
def printMsg(logStream, msg: str, level: str = ""):
    header = ""
    if level != "":
        header = F"   {level[:1].upper()}{level[1:]}: "
    if level != "debug":
        print(F"{header}{msg}")
    if logStream != None:
        logStream.write(F"{header}{msg}\n")

# Dumps a dictionary to screen
def dumpToLog(value: Any) -> None:
    if traceFlag:
        print("")
    for line in json.dumps(value, indent=4, ensure_ascii=False).split("\n"):
        if not(line.startswith("[") or line.startswith("]")):
            if '"type":' in line:
                line += F" ({typeLib})"
            if '"subtype":' in line:
                line += F" ({subTypeLib})"
            if '"switchtype":' in line:
                line += F" ({switchTypeLib})"
            if traceFlag:
                print(line)

# Return a path in a dictionary (else None)
def getPathValue(dict: Any, path: str, separator: str = '/') -> Any:
    pathElements = path.split(separator)
    element = dict
    for pathElement in pathElements:
        if pathElement not in element:
            return None
        element = element[pathElement]
    return element

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

# Check if a token is present in root device or in one of its sub device
def hasTokenPresent(nodeItems, itemName):
    # Does item exist in nodeItems?
    if itemName in nodeItems:
        return True
    # Scan all sub devices
    subDevices = getValue(nodeItems, "subdevices", {})
    for subDeviceKey in subDevices:
        # Does item exist in this sub device?
        if itemName in subDevices[subDeviceKey]:
            return True
    # Nothing found
    return False

# Format json data, removing {} and ""
def formatJson(jsonData: dict) -> str:
    return json.dumps(jsonData, ensure_ascii=False).replace("{", "").replace("}","").replace('"', "")

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

# *** Main code ***

# Extract this script file name
cdeFile = pathlib.Path(__file__).stem
currentPath = pathlib.Path(__file__).parent.resolve()

# Set current working directory to this python file folder
os.chdir(currentPath)

print(F"{cdeFile} V{codeVersion} - Use --trace to get details")
inputFiles = []
traceFlag = False
domoticzTypesFile = "DomoticzTypes.json"
domoticzTypesJson = {}
typeLib = ""
subTypeLib = ""
switchTypeLib = ""
logStream = None
checkV1File = FF_checkV1File()

# Use command line if given
if sys.argv[1:]:
    command = sys.argv[1:]
else:
    command = []

# Read arguments
helpMsg = 'Usage: ' + cdeFile + ' [options]' + """
    [--input=<input file(s)>]: input file name (can be repeated, default to *.json)
    [--trace]: enable trace
    [--help]: print this help message

   Check MqttMapper JSON files

"""
try:
    opts, args = getopt.getopt(command, "hti=",["help", "trace", "input="])
except getopt.GetoptError as excp:
    print(excp.msg)
    print('in >'+str(command)+'<')
    print(helpMsg)
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(helpMsg)
        sys.exit()
    elif opt in ("t", "--trace"):
        traceFlag = True
    elif opt in ('i=', '--input'):
        inputFiles.append(arg)

if not inputFiles:
    inputFiles.append('*.json')

if traceFlag:
    print('Input file(s)->'+str(inputFiles))

# Read Domoticz types
with open(domoticzTypesFile, "rt", encoding="UTF-8") as typesStream:
    try:
        domoticzTypesJson = json.load(typesStream)
    except Exception as error:
        print(F"{error} when reading {domoticzTypesFile}")

# Read config files
for specs in inputFiles:
    for configFile in glob.glob(specs):
        if configFile != domoticzTypesFile:
            try:
                with open(configFile, "rt", encoding = 'UTF-8') as configStream:
                    jsonData = json.load(configStream)
            except Exception as exception:
                if traceFlag:
                    logStream = open(pathlib.Path(configFile).stem+".log", "wt", encoding="utf-8")
                printMsg(logStream, str(exception)+" when loading "+configFile+". Fix this and retry check!!!", "error")
            else:
                fileFormat = "1.0"
                parameters = getValue(jsonData, "[parameters]", None)
                fileFormat = getValue(parameters, "version", "1.0")
                if traceFlag:
                    logStream = open(pathlib.Path(configFile).stem+".log", "wt", encoding="utf-8")
                errorSeen, messages = checkV1File.checkV1Json(jsonData, configFile, domoticzTypesJson)
                if errorSeen:
                    jsonData = {}
                    printMsg(logStream, F"Error analysing V{fileFormat} file {configFile}")
                    for elements in messages:
                        printMsg(logStream, elements[1], elements[0])
                else:
                    if messages != []:
                        printMsg(logStream, F"Information analysing V{fileFormat} file {configFile}")
                        for elements in messages:
                            originalElements = elements
                            printMsg(logStream, elements[1], elements[0])
            if logStream != None:
                logStream.close()