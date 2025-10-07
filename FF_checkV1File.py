# MqttMapper V1.0 file format checks
import json
from typing import Tuple, Any, List
from DomoticzTypes import DomoticzTypes

class FF_checkV1File:
    # Class initialization
    def __init__(self):
        self.fileVersion = "25.7.25-1"                              # File version
        self.errorSeen = False;                                     # Do we seen an error ?
        self.allMessages = []                                       # All messages to be printed
        self.switchTypes = DomoticzTypes()                          # Load types functions

    # Prints an error message, saving it and setting error flag
    def printError(self, message: str) -> None:
        self.allMessages.append(["error", message])
        self.errorSeen = True

    # Prints an info message
    def printInfo(self, message: str) -> None:
        self.allMessages.append(["info", message])

    # Prints a warning message
    def printWarning(self, message: str) -> None:
        self.allMessages.append(["warning", message])

    # Add a debug message
    def printDebug(self, message: str) -> None:
        self.allMessages.append(["debug", message])

    # Returns a dictionary value giving a key or default value if not existing
    def getValue(self, searchDict, searchKey, defaultValue: Any =''):
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

    # Return number of items in a ";" separated string (or zero if not string)
    def getItemCount(self, item: Any) -> int:
        if isinstance(item, str):                                   # Is item a string?
            parts = item.split(";")                                 # Split string giving ";"
            return len(parts)                                       # Return item count (1 if no ";" found)
        return 0                                                    # Not a string, return 0

    # Returns a field value in a dictionary with a selection field and value (or None if not found)
    def getDictField(self, searchDict: dict, returnField: str, selectField: str, selectValue: Any, selectField2: str = "", selectValue2 : Any = None) -> Any:
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
                                    return self.getValue(itemData, returnField, None)
                                else:
                                    return itemData
                    else:
                        # Return required field value
                        if returnField != "":
                            return self.getValue(itemData, returnField, None)
                        else:
                            return itemData
        return None

    # Display a list under readable format
    def formatList(self, listToDisplay: List[str]):
        toDisplay = ""
        for i in range(len(listToDisplay)):
            if toDisplay != "":
                toDisplay += " or "
            toDisplay += listToDisplay[i]
        return toDisplay

    # Check a json item against a definition dictionary (V1)
    def checkV1Token(self, tokenList, tokenName: str, nodeItem: Any, fullPath: str = ""):
        #  Check for mandatory tokens
        for token in tokenList:
            elements = token.split("/")
            # Is this token the one for our items?
            if elements[0] == tokenName:
                # If token mandatory?
                if tokenList[token]['mandatory']:
                    # Is token not present in items?
                    if not elements[1] in nodeItem:
                        self.printError(F"{elements[1]} is mandatory in >{fullPath}<")

        # Check for each item
        for item in nodeItem:
            # Compose key
            key = tokenName + "/" + item
            # For commands at root level, overwrite command name by "xxx"
            elements = fullPath.split(":")
            if len(elements) == 2 and elements[1] == "commands":
                key = tokenName + "/" + "xxx"
            elif len(elements) == 3 and elements[1] == "commands":
                key = "xxx" + "/" + item
            # Is item in allowed token list?
            if key in tokenList:
                # Check for item type against token type
                tokenTypeInitial = tokenList[key]['type']
                if not isinstance(tokenTypeInitial, list):
                    tokenTypeInitial = [tokenTypeInitial]
                tokenType = list(tokenTypeInitial)
                if tokenType != ["any"]:
                    # Get item type
                    itemType = type(nodeItem[item]).__name__
                    # Check for type
                    if itemType not in tokenType:
                        self.printError(F"{item} is {itemType} instead of {self.formatList(tokenType)} in >{fullPath}<")
                    if itemType == 'dict':
                        self.checkV1Token(tokenList, item, nodeItem[item], fullPath + ":" + item)
                    # We have a list, scan for each element against original type"²
                    if itemType == 'list':
                        # Remove list from allowed token types
                        if "list" in tokenType:
                            tokenType.remove("list")
                        for listElement in item:
                            # Get item type
                            itemType = type(listElement).__name__
                            # Check for type
                            if itemType not in tokenType:
                                self.printError(F"{item} is {itemType} instead of {self.formatList(tokenType)} in >{fullPath}<")
                            if itemType == 'dict':
                                self.checkV1Token(tokenList, item, listElement, fullPath + ":" + item)
            else:
                self.printError(F"{item} is unknown in >{fullPath}<")

    # Check MqttMapper V1 JSON mapping file jsonFile (returns True if errors found)
    def checkV1Json(self, jsonData: dict, jsonFile: str, domoticzTypesJson: dict) -> Tuple[bool, List[str]]:
        nodeTokenList = dict({
            "node/topic": {"mandatory":  True, "type":  "str"},
            "node/type": {"mandatory":  True, "type":  ["int", "str"]},
            "node/subtype": {"mandatory":  True, "type":  ["int", "str"]},
            "node/mapping": {"mandatory":  True, "type":  "dict"},
                "mapping/item": {"mandatory":  True, "type":  "str"},
                "mapping/default": {"mandatory":  False, "type":  ["int", "float", "str"]},
                "mapping/digits": {"mandatory":  False, "type":  ["int", "str"]},
                "mapping/multiplier": {"mandatory":  False, "type":  ["int", "float", "str"]},
                "mapping/values": {"mandatory":  False, "type":  "any"},
                "mapping/battery": {"mandatory":  False, "type":  "str"},
            "node/key": {"mandatory":  False, "type":  "str"},
            "node/throttle": {"mandatory":  False, "type":  "int"},
            "node/switchtype": {"mandatory":  False, "type":  ["int", "str"]},
            "node/options": {"mandatory":  False, "type":  "any"},
            "node/initial": {"mandatory":  False, "type":  "dict"},
                "initial/nvalue": {"mandatory":  False, "type":  ["int", "str"]},
                "initial/svalue": {"mandatory":  False, "type":  "str"},
            "node/restrictupdate" : {"mandatory":  False, "type":  "bool"},
            "node/visible": {"mandatory":  False, "type":  "bool"},
            "node/set": {"mandatory":  False, "type":  "dict"},
                "set/topic": {"mandatory":  False, "type":  "str"},
                "set/retain": {"mandatory":  False, "type":  "bool"},
                "set/payload": {"mandatory":  False, "type":  "any"},
                "set/command": {"mandatory":  False, "type":  "str"},
                "set/digits": {"mandatory":  False, "type":  ["int", "str"]},
                "set/multiplier": {"mandatory":  False, "type":  ["int", "float", "str"]},
                "set/mapping": {"mandatory":  False, "type":  "any"},
            "node/commands": {"mandatory":  False, "type":  "dict"},
            "node/select": {"mandatory":  False, "type":  "dict"},
                "select/item": {"mandatory":  True, "type":  "str"},
                "select/value": {"mandatory":  False, "type":  ["str", "list"]},
            "node/reject": {"mandatory":  False, "type":  "dict"},
                "reject/item": {"mandatory":  True, "type":  "str"},
                "reject/value": {"mandatory":  False, "type":  ["str", "list"]},
            "commands/xxx": {"mandatory":  False, "type":  "dict"},
                "xxx/topic": {"mandatory":  False, "type":  "str"},
                "xxx/retain": {"mandatory":  False, "type":  "bool"},
                "xxx/payload": {"mandatory":  False, "type":  "any"},
                "xxx/command": {"mandatory":  False, "type":  "str"}
        })

        self.errorSeen = False;                                     # Do we seen an error ?
        self.allMessages = []                                       # All messages to be printed
        # Iterating through the JSON list
        self.printDebug(F"Checking (V1) {jsonFile}")
        self.printDebug("\n" + json.dumps(jsonData, ensure_ascii=False, indent=4))
        devices = []
        global typeLib
        global subTypeLib
        global switchTypeLib
        for node in jsonData.items():
            # Load authorized token list
            nodeName = node[0]
            nodeItems = node[1]
            if nodeName == None or nodeName == '':
                self.printError(F'No device name given')
            elif nodeItems == None or nodeItems == '':
                self.printError(F'No items given for {nodeName}')
            else:
                self.checkV1Token(nodeTokenList, "node", nodeItems, node[0])
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
                        value = self.getDictField(domoticzTypesJson["types"], "name", "value", type)
                        if value != None:
                            typeLib = value

                    if typeLib == "???":
                        self.printError(F"Type {type} not known for {nodeName}")

                if "subtype" in nodeItems:
                    try:
                        subType = int(nodeItems["subtype"])
                    except:
                        pass
                    else:
                        value = self.getDictField(domoticzTypesJson["subTypes"], "name", "value", subType, "typeValue", type)
                        if value != None:
                            subTypeLib = value

                # Check for throttle parameter
                if "throttle" in nodeItems:
                    # Only one value given on digits
                    try:
                        delay = int(nodeItems["throttle"])
                    except:
                        self.printError(F'Invalid numeric value in "throttle": {nodeItems["throttle"]} for {nodeName}')
                    else:
                        if delay < 1:
                            self.printError(F'"Throttle" must be at least 1 second (is {nodeItems["throttle"]})')

                # Put a warning if no default specified when values are given in mapping
                if "mapping" in nodeItems:
                    mappingItems = nodeItems["mapping"]
                    if "values" in mappingItems and "default" not in mappingItems:
                        self.printWarning(F"It may be a good idea to specify 'mapping/default' when using 'mapping/values' for {nodeName}")

                # Look for type definition
                definitionItems = self.getDictField(domoticzTypesJson["definitions"], "", "typeValue", type)
                # If we have at least one type definition
                if definitionItems != None:
                    # Is this type not associated with a particular sub type?
                    if not definitionItems["noSubType"]:
                        # Type has specific sub type, search for this sub type
                        definitionItems = self.getDictField(domoticzTypesJson["definitions"], "", "typeValue", type, "subTypeValue", subType)
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
                                                value = self.getDictField(domoticzTypesJson["switchTypes"], "name", "value", switchType)
                                                # Save value or put an error message
                                                if value != None:
                                                    switchTypeLib = value
                                                else:
                                                    self.printError(F"switchType {switchType} is not a known switch type for type {type}, sub type {subType} for {nodeName}")
                                        #  There is a switch type in definition, value is meter
                                            elif definitionItems["switchType"] == "meter":
                                                # Check that configuration value exists in switch types definition
                                                value = self.getDictField(domoticzTypesJson["meterTypes"], "name", "value", switchType)
                                                # Save value or put an error message
                                                if value != None:
                                                    switchTypeLib = value
                                                else:
                                                    self.printError(F"switchType {switchType} is not a known meter type for type {type}, sub type {subType} for {nodeName}")
                                            # User specified a switch type while no defined
                                            elif switchType:
                                                self.printWarning(F"switchType should be 0, not {switchType} for type {type}, sub type {subType} for {nodeName}")
                                        else:
                                            # User specified a switch type while no defined
                                            if switchType != 0:
                                                self.printWarning(F"switchType should be 0, not {switchType} for type {type}, sub type {subType} for {nodeName}")
                                        # Check for multiple sValues
                                        if "sValue2" in definitionItems:
                                            if "initial" in nodeItems:
                                                if "svalue" not in nodeItems["initial"]:
                                                    self.printWarning(F'Type {type}, sub type {subType} has multiple items sValue, but "initial/svalue" not found for {nodeName}')
                                            else:
                                                self.printWarning(F'Type {type}, sub type {subType} has multiple items sValue, but "initial/svalue" not found for {nodeName}')
                                    else:
                                        self.printError(F"Type {type}, sub type {subType} not supported for {nodeName}")
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
                                givenValueCount = self.getItemCount(nodeItems["initial"]["svalue"])
                                if givenValueCount != sValueCount:
                                    self.printError(F"{givenValueCount} item{'s'[:givenValueCount^1]} given in 'initial/svalue' while {sValueCount} required for {nodeName}")
                        # Check for multiplier count if given
                        if "mapping" in nodeItems:
                            if "multiplier" in nodeItems["mapping"]:
                                givenValueCount = self.getItemCount(nodeItems["mapping"]["multiplier"])
                                if givenValueCount > 1 and givenValueCount != sValueCount:
                                    self.printError(F"{givenValueCount} item{'s'[:givenValueCount^1]} given in 'mapping/multiplier' while {sValueCount} required for {nodeName}")
                        # Check for digits count if given
                        if "mapping" in nodeItems:
                            if "digits" in nodeItems["mapping"]:
                                givenValueCount = self.getItemCount(nodeItems["mapping"]["digits"])
                                if givenValueCount > 1 and givenValueCount != sValueCount:
                                    self.printError(F"{givenValueCount} item{'s'[:givenValueCount^1]} given in 'mapping/digits' while {sValueCount} required for {nodeName}")
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
                                                self.printError(F'invalid numeric value in "digits": {nodeItems["mapping"]["digits"]}, element {i+1} for {nodeName}')
                                            else:
                                                # If this float value?
                                                if digitsList[i] != -1:
                                                    # If given value is not zero
                                                    if digitValue > digitsList[i]:
                                                        self.printWarning(F"Digit {i+1} is {digitValue}, should be no more than {digitsList[i]} for {nodeName}")
                                                else:
                                                    if digitValue > 0:
                                                        self.printWarning(F"Digit {i+1} is {digitValue}, should be zero for non float values for {nodeName}")
                                    else:
                                        # Only one value given on digits
                                        try:
                                            digitValue = int(nodeItems["mapping"]["digits"])
                                        except:
                                            self.printError(F'invalid numeric value in "digits": {nodeItems["mapping"]["digits"]} for {nodeName}')
                                        else:
                                            # For all sValues
                                            for i in range(len(digitsList)):
                                                # If this float value?
                                                if digitsList[i] != -1:
                                                    # If given value is not zero
                                                    if digitValue > digitsList[i]:
                                                        self.printWarning(F"Digit {i+1} is {digitValue}, should be no more than {digitsList[i]} for {nodeName}")
                device = self.getValue(nodeItems, 'key', self.getValue(nodeItems, 'topic', None))
                if device in devices:
                    self.printError(F"duplicate topic/key '{device}' found for {nodeName}")
                else:
                    devices.append(device)

        return self.errorSeen, self.allMessages