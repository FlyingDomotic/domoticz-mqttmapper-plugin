#!/usr/bin/python3
#   Parse MqttMapper configuration file
#

version = "1.2.0"

import glob
import os
import pathlib
import getopt
import sys
import json
from typing import Any

# Dumps a dictionary to screen
def dumpToLog(value: Any, depth: str = "") -> None:
    if isinstance(value, dict) or isinstance(value, list):
        for x in value:
            if isinstance(value[x], dict):
                print(depth+"> Dict '"+x+"' ("+str(len(value[x]))+"):")
                dumpToLog(value[x], depth+"--")
            elif isinstance(value[x], list):
                print(depth+"> List '"+x+"' ("+str(len(value[x]))+"):")
                dumpToLog(value[x], depth+"--")
            elif isinstance(value[x], str):
                print(depth+">'" + x + "':'" + str(value[x]) + "'")
            else:
                print(depth+">'" + x + "': " + str(value[x]))

# Return a path in a dictionary (else None)
def getPathValue (dict: Any, path: str, separator: str = '/') -> Any:
    pathElements = path.split(separator)
    element = dict
    for pathElement in pathElements:
        if pathElement not in element:
            return None
        element = element[pathElement]
    return element

# Returns a dictionary value giving a key or default value if not existing
def getValue(dict: Any, key: str, default : Any = '') -> Any:
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

# Check a json item against a definition dictinary
def checkToken(tokenName: str, nodeItem: Any) -> str:
    # Init errors
    errorText = ""

    # Load authorized token list
    tokenList = dict({ 
        "node/topic": {"mandatory": True, "type": "str"},
        "node/type": {"mandatory": True, "type": ["int", "str"]},
        "node/subtype": {"mandatory": True, "type": ["int", "str"]},
        "node/mapping": {"mandatory": True, "type": "dict"},
        "node/key": {"mandatory": False, "type": "str"},
        "node/switchtype": {"mandatory": False, "type": ["int", "str"]},
        "node/options": {"mandatory": False, "type": "Any"},
        "node/initial": {"mandatory": False, "type": "dict"},
        "node/visible": {"mandatory": False, "type": "bool"},
        "node/set": {"mandatory": False, "type": "dict"},
        "mapping/item": {"mandatory": True, "type": "str"},
        "mapping/default": {"mandatory": False, "type": "str"},
        "mapping/digits": {"mandatory": False, "type": "int"},
        "mapping/multiplier": {"mandatory": False, "type": ["int", "float"]},
        "mapping/values": {"mandatory": False, "type": "Any"},
        "set/topic": {"mandatory": False, "type": "str"},
        "set/payload": {"mandatory": False, "type": "Any"},
        "set/command": {"mandatory": False, "type": "str"},
        "set/digits": {"mandatory": False, "type": "int"},
        "set/multiplier": {"mandatory": False, "type": "int"},
        "initial/nvalue": {"mandatory": False, "type": "int"},
        "initial/svalue": {"mandatory": False, "type": "str"}
        })

    #  Check for mandatory tokens
    for token in tokenList:
        elements = token.split("/")
        # Is this token the one for our items?
        if elements[0] == tokenName:
            # If token mandatory?
            if tokenList[token]['mandatory']:
                # Is token not present in items?
                if not elements[1] in nodeItem:
                    errorText += F"\n{elements[1]} is mandatory"
                    if elements[0] != "node":
                        errorText += F" in {elements[0]}"

    # Check for each item
    for item in nodeItem:
        # Compose key
        key = tokenName + "/" + item
        # if item in allowed token list?
        if key in tokenList:
            # Check for item type against token type
            tokenType = tokenList[key]['type']
            if tokenType != "Any":
                # Get item type
                itemType = type(nodeItem[item]).__name__
                # Check for type 
                if isinstance(tokenType, list):
                    if itemType not in tokenType:
                        errorText += F"\n{item} is {itemType} instead of {tokenType}"
                else:
                    if itemType != tokenType:
                        errorText += F"\n{item} is {itemType} instead of {tokenType}"
                if itemType in ['list', 'dict']:
                    errorText += checkToken(item, nodeItem[item])
        else:
            errorText += F"\n{item} is unkown"
            if tokenName != "node":
                errorText += F" for {tokenName}"
    return errorText

# Check MqttMapper JSON mapping file jsonFile
def checkJson(jsonData: dict, jsonFile: str) -> None:
    # Iterating through the JSON list
    if traceFlag:
        dumpToLog(jsonData)
    print("Checking "+jsonFile)
    errorSeen = 0
    devices = []
    for node in jsonData.items():
        nodeName = node[0]
        nodeItems = node[1]
        nodeTopic = getValue(nodeItems, 'topic', None)
        nodeKey = getValue(nodeItems, 'key', None)
        errorText = ''
        if nodeName == None or nodeName == '':
            errorText += '\nno device name given'
        elif nodeItems == None or nodeItems == '':
            errorText += '\nno items given'
        else:
            errorText += checkToken("node", nodeItems)
        if errorText:
            print("    Invalid data in "+str(node))
            for errorLine in errorText[1:].split('\n'):
                print("    --> "+errorLine)
            errorSeen += 1
        device = nodeKey if nodeKey else nodeTopic
        if device in devices:
            print('Duplicate '+str(device)+ ' node/key found')
        else:
            devices.append(device)
    if errorSeen:
        print("    Errors in "+jsonFile+", fix them and recheck!!!")
    else:
        print("    File seems good")

# *** Main code ***
# Init arguments variables
cdeFile = __file__
if cdeFile[:2] == './':
    cdeFile = cdeFile[2:]

print(F"{cdeFile} V{version}")
inputFiles = []
traceFlag = False

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

# Set current working directory to this python file folder
os.chdir(pathlib.Path(__file__).parent.resolve())

# Read config files
for specs in inputFiles:
    for configFile in glob.glob(specs):
        try:
            with open(configFile, encoding = 'UTF-8') as configStream:
                checkJson(json.load(configStream), configFile)
        except Exception as exception:
            print(str(exception)+" when loading "+configFile+". Fix error and retry check!!!")