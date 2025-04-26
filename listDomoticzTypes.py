#!/usr/bin/python3
#   List all Domoticz supported types, sub types and switch types

version = "25.4.26-1"

import json
import pathlib
import os
from DomoticzTypes import DomoticzTypes

# Format json data, removing {} and ""
def formatJson(jsonData: dict) -> str:
    return json.dumps(jsonData, ensure_ascii=False).replace("{", "").replace("}","").replace('"', "")

# Extract value from dictionary, return "" if don't exists
def getValue(data, key):
    return data[key] if key in data else ""

# Print data line
def printData():
    global linePrinted
    linePrinted = True
    outStream.write(F"{typeValue}\t{typeName}\t{subTypeValue}\t{subTypeName}\t{switchTypeValue}\t{switchTypeName}\t{itemType}\t{itemName}\t{itemUnit}\t{itemDataType}\t{itemDigits}\n")

# ===== Main code =====

# Set current working directory to this python file folder
currentPath = pathlib.Path(__file__).parent.resolve()
os.chdir(currentPath)

# Get command file name (without suffix)
currentFileName = pathlib.Path(__file__).stem

# Load Domoticz types dictionary
typesFile = "DomoticzTypes.json"
jsonData = {}
switchTypes = DomoticzTypes()

try:
    with open(typesFile, "rt", encoding="UTF-8") as inpStream:
        jsonData = json.load(inpStream)
except Exception as exception:
    print(str(exception)+" when loading "+typesFile)
    exit(2)

outStream = open(currentFileName+".txt", "wt", encoding="utf-8")
typeValue = "Type"
typeName = "Type name"
subTypeValue = "SubType"
subTypeName = "SubType name"
switchTypeValue = "SwitchType"
switchTypeName = "SwitchType name"
itemType = "Data"
itemName = "Data name"
itemUnit= "Data unit"
itemDataType = "Data type"
itemDigits = "Data digits"
printData()

# Scan all definitions
for key in jsonData["definitions"].keys():
    item = jsonData["definitions"][key]
    typeValue = getValue(item, "typeValue")
    typeName = getValue(item, "typeName")
    subTypeValue = getValue(item, "subTypeValue")
    subTypeName = getValue(item, "subTypeName")
    switchCategory = getValue(item, "switchType")
    linePrinted = False
    switchTypeName = ""
    switchTypeValue = ""
    switchName = ""
    itemName = ""
    itemUnit = ""
    itemDataType = ""
    itemDigits = ""
    if switchCategory != "":
        for key2 in jsonData[F'{switchCategory}Types']:
            item2 = jsonData[F'{switchCategory}Types'][key2]
            switchTypeValue = getValue(item2, "value")
            switchTypeName = getValue(item2, "name")
            for itemType in item.keys():
                if itemType == "nValue":
                    items = item[itemType]
                    itemName = getValue(items, "name")
                    itemUnit = getValue(items, "unit")
                    itemDataType = getValue(items, "dataType")
                    itemDigits = getValue(items, "digits")
                    printData()
                if itemType == "sValue" and (switchCategory != "switch" or switchTypes.isLevelSwitch(typeValue, subTypeValue, switchTypeValue)):
                    items = item[itemType]
                    itemName = getValue(items, "name")
                    itemUnit = getValue(items, "unit")
                    itemDataType = getValue(items, "dataType")
                    itemDigits = getValue(items, "digits")
                    printData()
    else:
        for itemType in item.keys():
            if itemType == "nValue":
                items = item[itemType]
                itemName = getValue(items, "name")
                itemUnit = getValue(items, "unit")
                itemDataType = getValue(items, "dataType")
                itemDigits = getValue(items, "digits")
                printData()
            if itemType == "sValue":
                items = item[itemType]
                itemName = getValue(items, "name")
                itemUnit = getValue(items, "unit")
                itemDataType = getValue(items, "dataType")
                itemDigits = getValue(items, "digits")
                printData()
    if not linePrinted:
        printData()

outStream.close()
