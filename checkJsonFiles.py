#!/usr/bin/python3
#   Parse MqttMapper configuration file
#

import glob
import os
import pathlib
import getopt
import sys
import json

# Dumps a dictionary to screen
def dumpToLog(value, Depth=""):
    if isinstance(value, dict) or isinstance(value, list):
        for x in value:
            if isinstance(value[x], dict):
                print(Depth+"> Dict '"+x+"' ("+str(len(value[x]))+"):")
                dumpToLog(value[x], Depth+"--")
            elif isinstance(value[x], list):
                print(Depth+"> List '"+x+"' ("+str(len(value[x]))+"):")
                dumpToLog(value[x], Depth+"--")
            elif isinstance(value[x], str):
                print(Depth+">'" + x + "':'" + str(value[x]) + "'")
            else:
                print(Depth+">'" + x + "': " + str(value[x]))

# Return a path in a dictionary (else None)
def getPathValue (dict, path, separator = '/'):
    pathElements = path.split(separator)
    element = dict
    for pathElement in pathElements:
        if pathElement not in element:
            return None
        element = element[pathElement]
    return element

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


# Check MqttMapper JSON mapping file jsonFile
def checkJson(jsonData, jsonFile):
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
        nodeType = getValue(nodeItems, 'type', None)
        nodeKey = getValue(nodeItems, 'key', None)
        nodeSubtype = getValue(nodeItems, 'subtype', None)
        nodeSwitchtype = getValue(nodeItems, 'switchtype', None)
        nodeOptions  = getValue(nodeItems, 'options', None)
        nodeMapping = getValue(nodeItems, 'mapping', None)
        mappingItem = getValue(nodeMapping, 'item', None)
        mappingDefault = getValue(nodeMapping, 'default', None)
        mappingValues = getValue(nodeMapping, 'values', None)
        errorText = ''
        if nodeName == None or nodeName == '':
            errorText += ', no device name given'
        elif nodeItems == None or nodeItems == '':
            errorText += ', no items given'
        else:
            if nodeType == None:
                errorText += ', no type given'
            if nodeSubtype == None:
                errorText += ', no subtype given'
                if nodeMapping == None:
                    errorText += ", no mapping given"
                else:
                    if mappingItem == None:
                        errorText += ', no mapping item given'
        if errorText:
            print('Invalid data in "'+str(node)+'": '+errorText[1:])
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
except getopt.GetopterrorText as excp:
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