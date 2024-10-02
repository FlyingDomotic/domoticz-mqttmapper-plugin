#!/usr/bin/python3
#   Display Domoticz supported types, sub types and switch types
#

import json
import re
import pathlib
import os
from typing import Any, Tuple, Union, Optional

version = "1.1.0"

# Returns a dictionary value giving a key or default value if not existing
def getValue(dict: Any, key: str, default : Optional[Any] = '') -> Any:
    if dict != None and key in dict:
        return dict[key]
    return default

# Converts an integer value into hexa string on an odd length (0x12 or 0x1234 or 0x123456...)
def makeHexa(value: int) -> str:
    try:
        result = hex(value)
    except:
        return ""
    length = len(result)
    if (length & 1):
        result = result[:2]+"0"+result[2:]
    return result
    
# Convert a value (hexa or integer) representing an integer to integer (or default)
def makeInt(value: Any, default: Any = None) -> Union[int, None]:
    # If value is string
    if isinstance(value, str):
        # Hexa value if starting by "0x" or "0X"
        if value.lower().startswith("0x"):
            # Try to convert to interger
            try:
                return int(value,16)
            # Return default if incorrect hex integer
            except:
                return default
    # If value is not string, try to convert to integer
    try:
        return int(value)
    # Return default if incorrect integer
    except:
        return default

# Format json data, removing {} and ""
def formatJson(jsonData: dict) -> str:
    return json.dumps(jsonData, ensure_ascii=False).replace("{", "").replace("}","").replace('"', "")

# Analyze a string, and return integer value (or None if not integer) and re.compile value
def analyzeInput(inp: str) -> Tuple[Union[int, None], Any]:
    intResult = None
    if inp != "":
        intResult = makeInt(inp)
    try:
        findResult = re.compile(inp, re.IGNORECASE)
    except Exception as error:
        print (F"{error} when analyzing {inp} - Will be replaced by '.*'")
        findResult = re.compile(".*", re.IGNORECASE)

    return intResult, findResult

# ===== Main code =====

# Set current working directory to this python file folder
currentPath = pathlib.Path(__file__).parent.resolve()
os.chdir(currentPath)

# Get command file name (without suffix)
currentFileName = pathlib.Path(__file__).stem

# Load Domoticz types dictionary
typesFile = "DomoticzTypes.json"
jsonData = {}
try:
    with open(typesFile, "rt", encoding="UTF-8") as inpStream:
        jsonData = json.load(inpStream)
except Exception as exception:
    print(str(exception)+" when loading "+typesFile)
    exit(2)

# Write header
print(F"{pathlib.Path(__file__).stem} V{version}")
print("Specify either number ('123'), hexadecimal number ('0xf3'), string ('general') or regex ('.*'), separated by ','")
print("Enter ',,.*' to display everything")

# Get user input
while 1:
    try:
        answer = input("Type, subType, switchType: ")
    # Exit if any errors when getting input
    except:
        break
    # Exit if no input given
    if answer == "":
        break
    # Cleanup input
    answer = answer.replace("\t", "").replace(" ","").strip()+",,"
    # Split input in at least 3 parts
    parts = answer.split(",")

    # Extract 3 positional parameters
    type, typeFind = analyzeInput(parts[0])
    subType, subTypeFind = analyzeInput(parts[1])
    switchType, switchTypeFind = analyzeInput(parts[2])

    typeFound = False
    subTypeFound = False
    switchTypeFound = False

    # Scan all definitions
    typeList = []
    for key in jsonData["definitions"].keys():
        item = jsonData["definitions"][key]
        if (type != None and item["typeValue"] == type) or (type == None and typeFind.match(item["typeName"]) != None):
            typeFound = True
            if not item["typeValue"] in typeList:
                typeList.append(item["typeValue"])
                print(F'  Type {item["typeValue"]}: {item["typeName"]}')
            # Do we have a subType?
            if ("subTypeName" in item) or item["noSubType"]:
                if (subType != None and item["subTypeValue"] == subType) or (subType == None and (item["noSubType"] or subTypeFind.match(item["subTypeName"]) != None)):
                    subTypeFound = True
                    if "subTypeName" in item:
                        print(F'    Subtype {item["subTypeValue"]}: {item["subTypeName"]}')
                    else:
                        print(F'    Subtype {item["subTypeValue"]}: [Generic value]')
                    if "switchType" in item:
                        for key2 in jsonData[F'{item["switchType"]}Types']:
                            item2 = jsonData[F'{item["switchType"]}Types'][key2]
                            if (switchType != None and item2["value"] == switchType) or (switchType == None and switchTypeFind.match(item2["name"]) != None):
                                    switchTypeFound = True
                                    print(F'      Switchtype {item2["value"]}: {item2["name"]}')
            # Print nValue and sValue(s)
            for item2 in item.keys():
                if item2 == "nValue" or item2.startswith("sValue"):
                    items = item[item2]
                    # Remove format item
                    if "format" in items:
                        del items["format"]
                    print(f"        {item2}: {formatJson(items)}")