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

version = "1.3.11"

import glob
import os
import pathlib
import getopt
import sys
import json
from typing import Any

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

# Returns a field value in a dictionary with a selection field and value (or None if not found)
def getDictField(searchDict: dict, returnField: str, selectField: str, selectValue: Any, selectField2: str = "", selectValue2 : Any = None) -> Any:
    # Scan all items
    for item in searchDict.keys():
        # Extract data
        itemData = searchDict[item]
        # Is select field in item?
        if selectField in itemData:
            # Is select field with required value?
            if itemData[selectField] == selectValue:
                if selectField2 != "":
                    # Is select field 2 in item?
                    if selectField2 in itemData:
                        # Is select field 2 with required value?
                        if itemData[selectField2] == selectValue2:
                            # Return required field value
                            if returnField != "":
                                return getValue(itemData, returnField, None)
                            else:
                                return itemData
                else:
                    # Return required field value
                    if returnField != "":
                        return getValue(itemData, returnField, None)
                    else:
                        return itemData
    return None

# Return number of items in a ";" separated string (or zero if not string)
def getItemCount(item: Any) -> int:
    if type(item).__name__ == "str":                            # Is item a string?
        parts = item.split(";")                                 # Split string giving ";"
        return len(parts)                                       # Return item count (1 if no ";" found)
    return 0                                                    # Not a string, return 0

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
def getValue(dict: Any, key: str, default: Any = '') -> Any:
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

# Format json data, removing {} and ""
def formatJson(jsonData: dict) -> str:
    return json.dumps(jsonData, ensure_ascii=False).replace("{", "").replace("}","").replace('"', "")

# Check a json item against a definition dictionary
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
        "mapping/digits": {"mandatory": False, "type": ["int", "str"]},
        "mapping/multiplier": {"mandatory": False, "type": ["int", "float", "str"]},
        "mapping/values": {"mandatory": False, "type": "Any"},
        "set/topic": {"mandatory": False, "type": "str"},
        "set/payload": {"mandatory": False, "type": "Any"},
        "set/command": {"mandatory": False, "type": "str"},
        "set/digits": {"mandatory": False, "type": ["int", "str"]},
        "set/multiplier": {"mandatory": False, "type": ["int", "float", "str"]},
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
            errorText += F"\n{item} is unknown"
            if tokenName != "node":
                errorText += F" for {tokenName}"
    return errorText

# Check MqttMapper JSON mapping file jsonFile
def checkJson(jsonData: dict, jsonFile: str) -> None:
    # Don't check DomoticzTypes.json file
    if jsonFile == domoticzTypesFile:
        return
    # Iterating through the JSON list
    print("Checking "+jsonFile)
    errorSeen = 0
    warningSeen = 0
    devices = []
    global typeLib
    global subTypeLib
    global switchTypeLib
    for node in jsonData.items():
        errors = 0
        warnings = 0
        nodeName = node[0]
        nodeItems = node[1]
        nodeTopic = getValue(nodeItems, 'topic', None)
        nodeKey = getValue(nodeItems, 'key', None)
        errorText = ''
        warningText = ''
        if nodeName == None or nodeName == '':
            errorText += '\nno device name given'
            errors += 1
        elif nodeItems == None or nodeItems == '':
            errorText += '\nno items given'
            errors += 1
        else:
            newErrors = checkToken("node", nodeItems)
            if newErrors != "":
                errorText += newErrors
                errors += len(errorText.split("\n")) - 1
        if traceFlag:
            dumpToLog(node)
        type = None
        typeLib = "???"
        subType = None
        subTypeLib = "???"
        definitionItems = None
        switchType = None
        switchTypeLib = "???"

        if "type" in nodeItems:
            try:
                type = int(nodeItems["type"])
            except:
                pass
            else:
                value = getDictField(domoticzTypes["types"], "name", "value", type)
                if value != None:
                    typeLib = value

            if typeLib == "???":
                errorText += F"\ntype {type} not known"
                errors += 1

        if "subtype" in nodeItems:
            try:
                subType = int(nodeItems["subtype"])
            except:
                pass
            else:
                value = getDictField(domoticzTypes["subTypes"], "name", "value", subType, "typeValue", type)
                if value != None:
                    subTypeLib = value

            if subTypeLib == "???":
                errorText += F"\nsubType {subType} not known with type {type}"
                errors += 1

       # Put a warning if no default specified when values are given in mapping
        if "mapping" in nodeItems:
            mappingItems = nodeItems["mapping"]
            if "values" in mappingItems and "default" not in mappingItems:
                warningText += "\nIt may be a good idea to specify 'mapping/default' when using 'mapping/values'"
                warnings += 1

        # Look for type definition
        definitionItems = getDictField(domoticzTypes["definitions"], "", "typeValue", type)
        # If we have at least one type definition
        if definitionItems != None:
            # Is this type not associated with a particular sub type?
            if not definitionItems["noSubType"]:
                # Type has specific sub type, search for this sub type
                definitionItems = getDictField(domoticzTypes["definitions"], "", "typeValue", type, "subTypeValue", subType)
                if definitionItems != None:
                    # Do we have an associated switch type?
                    if "switchtype" in nodeItems:
                        try:
                            switchType = int(nodeItems["switchtype"])
                        except:
                            pass
                        else:
                            # When having definition items
                            if definitionItems != None:
                                # Check for switch type
                                if "switchType" in definitionItems:
                                    #  There is a switch type in definition, value is switch
                                    if definitionItems["switchType"] == "switch":
                                        # Check that configuration value exists in switch types definition
                                        value = getDictField(domoticzTypes["switchTypes"], "name", "value", switchType)
                                        # Save value or put an error message
                                        if value != None:
                                            switchTypeLib = value
                                        else:
                                            errorText += F"\nswitchType {switchType} is not a known switch type for type {type}, sub type {subType}"
                                            errors += 1
                                #  There is a switch type in definition, value is meter
                                    elif definitionItems["switchType"] == "meter":
                                        # Check that configuration value exists in switch types definition
                                        value = getDictField(domoticzTypes["meterTypes"], "name", "value", switchType)
                                        # Save value or put an error message
                                        if value != None:
                                            switchTypeLib = value
                                        else:
                                            errorText += F"\nswitchType {switchType} is not a known meter type for type {type}, sub type {subType}"
                                            errors += 1
                                    # User specified a switch type while no defined
                                    elif switchType:
                                        warningText += F"\nswitchType should be 0, not {switchType} for type {type}, sub type {subType}"
                                        warnings += 1
                                else:
                                    # User specified a switch type while no defined
                                    if switchType != 0:
                                        warningText += F"\nswitchType should be 0, not {switchType} for type {type}, sub type {subType}"
                                        warnings += 1
                                # Check for multiple sValues
                                if "sValue2" in definitionItems:
                                    if "initial" in nodeItems:
                                        if "svalue" not in nodeItems["initial"]:
                                            warningText += F'\nType {type}, sub type {subType} has multiple items sValue, but "initial/svalue" not found'
                                            warnings += 1
                                    else:
                                        warningText += F'\nType {type}, sub type {subType} has multiple items sValue, but "initial/svalue" not found'
                                        warnings += 1
                            else:
                                errorText += F"\nType {type}, sub type {subType} not supported!"
                                errors += 1
            # Compute sValue item count associated with this type/sub type
            sValueCount = 0
            # Count all sValue dans save each digit count for floats
            if definitionItems != None:
                digitsList = []
                for item in definitionItems.keys():
                    if item.startswith("sValue"):
                        if definitionItems[item]["dataType"] == "floating point number":
                            if "digits" in definitionItems[item]:
                                # Insert digit count
                                digitsList.append(definitionItems[item]["digits"])
                            else:
                                # 0 means float without decimals
                                digitsList.append(0)
                        else:
                            # -1 means not float
                            digitsList.append(-1)
                        sValueCount += 1
                # Check for initial sValue items if given
                if "initial" in nodeItems:
                    if "svalue" in nodeItems["initial"]:
                        givenValueCount = getItemCount(nodeItems["initial"]["svalue"])
                        if givenValueCount != sValueCount:
                            errorText += F"\n{givenValueCount} item{'s'[:givenValueCount^1]} given in 'initial/svalue' while {sValueCount} required"
                            errors += 1
                # Check for multiplier count if given
                if "mapping" in nodeItems:
                    if "multiplier" in nodeItems["mapping"]:
                        givenValueCount = getItemCount(nodeItems["mapping"]["multiplier"])
                        if givenValueCount > 1 and givenValueCount != sValueCount:
                            errorText += F"\n{givenValueCount} item{'s'[:givenValueCount^1]} given in 'mapping/multiplier' while {sValueCount} required"
                            errors += 1
                # Check for digits count if given
                if "mapping" in nodeItems:
                    if "digits" in nodeItems["mapping"]:
                        givenValueCount = getItemCount(nodeItems["mapping"]["digits"])
                        if givenValueCount > 1 and givenValueCount != sValueCount:
                            errorText += F"\n{givenValueCount} item{'s'[:givenValueCount^1]} given in 'mapping/digits' while {sValueCount} required"
                            errors += 1
                        else:
                            # Check any given digit count less or equal of max digit, for floats (or zero for others)
                            if givenValueCount:
                                # Scan all elements in digits
                                i = -1
                                for part in nodeItems["mapping"]["digits"].split(";"):
                                    i += 1
                                    try:
                                        if part != "":
                                            digitValue = int(part)
                                        else:
                                            digitValue = 0
                                    except:
                                        errorText += F'\ninvalid numeric value in "digits": {nodeItems["mapping"]["digits"]}, element {i+1}'
                                        errors += 1
                                    else:
                                        # If this float value?
                                        if digitsList[i] != -1:
                                            # If given value is not zero
                                            if digitValue > digitsList[i]:
                                                warningText += F"\nDigit {i+1} is {digitValue}, should be no more than {digitsList[i]}"
                                                warnings += 1
                                        else:
                                            if digitValue > 0:
                                                warningText += F"\nDigit {i+1} is {digitValue}, should be zero for non float values"
                                                warnings += 1
                            else:
                                # Only one value given on digits
                                try:
                                    digitValue = int(nodeItems["mapping"]["digits"])
                                except:
                                    errorText += F'\ninvalid numeric value in "digits": {nodeItems["mapping"]["digits"]}'
                                    errors += 1
                                else:
                                    # For all sValues
                                    for i in range(len(digitsList)):
                                        # If this float value?
                                        if digitsList[i] != -1:
                                            # If given value is not zero
                                            if digitValue > digitsList[i]:
                                                warningText += F"\nDigit {i+1} is {digitValue}, should be no more than {digitsList[i]}"
                                                warnings += 1
        if traceFlag:
            if definitionItems != None:
                # List all nValue and sValue
                for item in definitionItems.keys():
                    if item == "nValue" or item.startswith("sValue"):
                        items = definitionItems[item]
                        # Remove format item
                        if "format" in items:
                            del items["format"]
                        print(f"    {item}: {formatJson(items)}")
        device = nodeKey if nodeKey else nodeTopic
        if device in devices:
            errorText += F"\nduplicate topic '{device}' node/key found"
            errors += 1
        else:
            devices.append(device)
        if errorText:
            print(F"    Error{'s'[:errors^1]} in {node}")
            for errorLine in errorText[1:].split('\n'):
                print("    --> "+errorLine)
            errorSeen += errors
        if warningText:
            print(F"    Warning{'s'[:warnings^1]} in {node}")
            for warningLine in warningText[1:].split('\n'):
                print("    --> "+warningLine)
            warningSeen += warnings
    if errorSeen:
        print(F"  Error{'s'[:errorSeen^1]} found in {jsonFile}, fix them and recheck!!!")
    elif warningSeen:
        print(F"  Warning{'s'[:warningSeen^1]} detected in {jsonFile}")
    else:
        print("  File seems good")

# *** Main code ***

# Init arguments variables
cdeFile = __file__
if cdeFile[:2] == './':
    cdeFile = cdeFile[2:]

print(F"{cdeFile} V{version} - Use --trace to get details")
inputFiles = []
traceFlag = False
domoticzTypesFile = "DomoticzTypes.json"
domoticzTypes = {}
typeLib = ""
subTypeLib = ""
switchTypeLib = ""

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
        domoticzTypes = json.load(typesStream)
    except Exception as error:
        print(F"{error} when reading {domoticzTypesFile}")

# Set current working directory to this python file folder
os.chdir(pathlib.Path(__file__).parent.resolve())

# Read config files
for specs in inputFiles:
    for configFile in glob.glob(specs):
        try:
            with open(configFile, encoding = 'UTF-8') as configStream:
                jsonData = json.load(configStream)
        except Exception as exception:
            print(str(exception)+" when loading "+configFile+". Fix error and retry check!!!")
        else:
            checkJson(jsonData, configFile)
