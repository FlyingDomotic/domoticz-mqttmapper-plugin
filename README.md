# MqttMapper Domoticz plug-in / plug-in MqttMapper pour Domoticz

[Cliquez ici pour la version française plus bas dans ce document(#Version française)

MqttMapper is a Domoticz Python plug-in allowing to map MQTT topics directly to Domoticz devices.

## What's for?
If you want to be able to read/write some MQTT topics and maps them to Domoticz devices, without having to install NodeRed, and/or integrate sensors that don't have HomeAssistant discovery item, this plug-in is made for you.

## Prerequisites

- Domoticz 2020.0 or higher (but lower version could also work)
- Make sure that your Domoticz supports Python plug-ins (https://wiki.domoticz.com/Using_Python_plugins)

## Installation

Follow these steps:

1. Clone repository into your Domoticz plug-ins folder
```
cd domoticz/plugins
git clone https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin.git MqttMapper
```
2. Restart Domoticz
3. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
4. Go to "Hardware" page and add new item with type "MqttMapper"
5. Set your MQTT server information to plug-in settings (address, port, username, password)
6. Give JSON configuration file name to be used (located in MqttMapper plug-in folder)

## Plug-in update

1. Go to plug-in folder and pull new version
```
cd domoticz/plugins/MqttMapper
git pull
```
2. Restart Domoticz

Note: if you did any changes to plug-in files and `git pull` command doesn't work for you anymore, you could stash all local changes using
```
git stash
```
or
```
git checkout <modified file>
```

## What's MQTT?

MQTT is a message exchange system based on queues allowing some applications/servers to send (publish)  messages to some other applications/clients who asked to receive (subscribe to) these messages.

As clients may not be connected when a message is sent, server may add the "retain" flag to  store the last copy of the message, to be sent when clients connects.

Lot of clients tools are able to read and write MQTT messages.  A popular one is MQTT Explorer (https://mqtt-explorer.com/). You may want to install one to have a look at what happens in MQTT broker.

Messages are sent with a name (topic), for example "zigbee2mqtt/bridge/config". In MqttMapper, this corresponds to "topic".

Topic points to  sent data. Here’s an example of "zigbee2mqtt/bridge/config" topic:

```
{"commit":"56589dc","coordinator":{"meta":{"maintrel":1,"majorrel":2,"minorrel":7,"product":1,"revision":20220221,"transportrev":2},"type":"zStack3x0"},"log_level":"debug","network":{"channel":15,"extendedPanID":"0xeb344dd381129444","panID":22046},"permit_join":false,"version":"1.34.0"}
```
As we can see, data is (very often) stored as JSON (but you may also have raw content like `20.5` or `on`).

Using JSON tools (like NotePad++ JSON extension or embedded JSON viewer in MQTT Explorer), this can be seen more friendly like:
```
{
	"commit": "56589dc",
	"coordinator": {
		"meta": {
			"maintrel": 1,
			"majorrel": 2,
			"minorrel": 7,
			"product": 1,
			"revision": 20220221,
			"transportrev": 2
		},
		"type": "zStack3x0"
	},
	"log_level": "debug",
	"network": {
		"channel": 15,
		"extendedPanID": "0xeb344dd381129444",
		"panID": 22046
	},
	"permit_join": false,
	"version": "1.34.0"
}
```
To get access to `channel` data (15), you must specify `item` in MqttMapper as `network/channel` and `revision` data (20220221) as `coordinator/meta/revision`.

When data is unstructured (or if you want to get full content of a message), specify `"item": ""` in MqttMapper.

To make it short, use MQTT client to have a view of MQTT tree, find full topic name and put it in `topic` in MqttMapper, find JSON data key into topic’s data and put it in `item` in MqttMapper (or set it empty if not JSON structured).

You should now have understood these two tricky things ;-)

## Configuration

Plug-in uses an external JSON configuration file to map MQTT topics to Domoticz devices. Here's an example of syntax:

```ts
{
    "Car windows": {
        "topic": "volvo/xx-999-xx/binary_sensor/any_window_open/state",
        "type": "244", "subtype": "73", "switchtype": "11",
        "mapping": {"item": "", "default": "1", "values": {"close": "0"}}
    },
    "Car lock": {
        "topic": "volvo/xx-999-xx/lock/lock/state",
        "type": "244", "subtype": "73","switchtype": "11",
        "mapping": {"item": "", "default": "0", "values": {"lock": "1"}}
    },
    "Car engine running": {
        "topic": "volvo/xx-999-xx/binary_sensor/is_engine_running/state",
        "type": "244", "subtype": "73", "switchtype": "8", 
        "mapping": {"item": "", "default": "1", "values": {"off": "0"}
        }
    },
    "Car odometer": {"topic": "volvo/xx-999-xx/sensor/odometer/state",
        "type": "113", "subtype": "0", "switchtype": "3",
        "options": {"ValueQuantity":"Distance", "ValueUnits":"km"},
        "mapping": {"item": ""}
    },
    "Car fuel amount": {"topic": "volvo/xx-999-xx/sensor/fuel_amount/state",
        "type": "243", "subtype": "31", "switchtype": "0",
        "options": {"Custom":"1;L"},
        "mapping": {"item": ""}
    },
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
		"select": {"item": "isOk", "value": "yes"},
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    },
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0;0;0"},
        "mapping": {"item": "temperature;humidity;~0", "multiplier": "0.1;1;1", "digits": "1;0;0", "battery": "batLevel"}
    },
    "Boiler power": {
        "topic": "boiler/SENSOR",
        "type": "248", "subtype": "1", "switchtype": "0",
		"throttle": 5,
        "mapping": {"item": "ENERGY/Power;ENERGY/Total"}}
    },
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}, "retain": false},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    },
    "Kontor takbelysning": {
		"topic": "shellies/shellypro4pm-xxxx/status/switch:0",
		"type": "244", "subtype": "73", "switchtype": "0",
		"mapping": {
			"item": "output",
			"default": "0",
			"values": {"False": "0", "True" : "100"}
		},
		"set": {
			"topic": "shellies/shellypro4pm-xxxx/rpc",
			"payload": "{ \"id\":0, \"src\": \"domoticz\", \"method\": \"Switch.Set\", \"params\":{\"id\":0,\"on\":#}}",
			"mapping": {"values": {"false": "0", "true" : "100"}}
		}
     }?
	"Test blind": {
		"topic": "blind/state",
		"type": "244", "subtype": "73", "switchtype": "21",
		"mapping": {"item": "value"},
		"commands": {
			"Open": {"topic": "blind/setOtherTopic", "payload": {"value": "Open"}},
			"Close": {"topic": "blind/setOtherTopic", "payload": {"value": "Close"}},
			"Stop": {"topic": "blind/setOtherTopic", "payload": {"value": "<command>"}},
			"Set Level":{"topic": "xxxx/setLevelTopic", "payload": "{\"value\": <level>}", "retain": true},
		}
	}
}
```

Let's see how this is constructed:

```ts
    "Car windows": {
        "topic": "volvo/xx-999-xx/binary_sensor/any_window_open/state",
        "type": "244", "subtype": "73", "switchtype": "11",
        "mapping": {"item": "", "default": "1", "values": {"close": "0"}}
    }

```

`Car windows` is the name of Domoticz device to be created. `type`, `subtype` and `switchtype` contains the type/subtype/switchtype values of device being created. Valid values can be found at (https://wiki.domoticz.com/Developing_a_Python_plugin#Available_Device_Types).

When empty or `~*`, `mapping` -> `item` indicates that payload is not in a JSON format. Extracted value is content of payload. Default value is set in `default` and mapping values in `values`. Here, when payload is `close`, device is set to `1`.

In short, when receiving topic `volvo/xx-999-xx/binary_sensor/any_window_open/state` with value `close`, a switch device `(244/73/11)` is set to off, else on.

When `default` is not specified, the extracted value will be directly loaded in associated device.

```ts
    "Car odometer": {"topic": "volvo/xx-999-xx/sensor/odometer/state",
        "type": "113", "subtype": "0", "switchtype": "3",
        "options": {"ValueQuantity":"Distance", "ValueUnits":"km"},
        "mapping": {"item": ""}
    }
```

Here, `options` contains the options used to create the device. Obviously, I don't find a full list, I put a partial one at end of this document. 

```ts
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
		"select": {"item": "isOk", "value": "yes"},
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    }
```

This time, payload is in JSON format (`item` is not empty). This mean that the value will be extracted from `temperature` payload item, at the root level. `ENERGY/Power` in later example means that value will be extracted in `Power` item of `Energy` root item.

`multiplier` is optional, and gives the factor to apply to numeric value (here `0.1`, equivalent to divided by 10). When having multiple items in sValue, you can use multiplier like "0.1;10;1".
'digits' is also optional, and gives the number of decimal digits to round value to. When having digits items in sValue, you can use digits like "1;2;0".

`select` allow to consider only message having a specific item with a given value (else message will be just ignored). Here, only message with `"isOk": "yes"` will be selected.

```ts
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0;0;0"},
        "mapping": {"item": "temperature;humidity;~0", "multiplier": "0.1;1;1", "digits": "1;0;0", "battery": "batLevel"}
    }
```

To specify multiple values, separate them with a `;`, like in `temperature;humidity`. Device value will be set with the concatenation of the two items.

Note that you also can specify constants in the list, prefixing them with `~`. For example `total;~0;~0;~0;power;~0` to generate a kWh counter sValue.

Should you want to change only part of sValue, you may use `~` alone to keep current value. For example, `value;~` will insert content of value item and keep second part of sValue.

To set initial sValue or nValue, you can use "initial": {"nvalue": 123} or "initial": {"svalue": "abc"} or both.

You can also specify "battery" followed by payload name to extract (here "batLevel") with same specification as "item"

You may need to create multiple devices from the same topic. In this case, use optional `key` item to specify a "virtual" key. This key can be anything, as long as it is unique and different from topics. For example:

```ts
{
     "mvtdec1": {
        "topic": "KC868_AI/1234567890/STATE",
        "key": "KC868_AI/1234567890/STATE-input1",
        "type": "244", "subtype": "73", "switchtype": "8",
        "mapping": {"item": "input1/value", "default": "0", "values": {"True": "1"}}
    },
     "mvtdec2": {
        "topic": "KC868_AI/1234567890/STATE",
        "key": "KC868_AI/1234567890/STATE-input2",
        "type": "244", "subtype": "73", "switchtype": "8",
        "mapping": {"item": "input2/value", "default": "0", "values": {"True": "1"}}
    }
}
```
will map properly a json payload as `{"input1":{"value":false},"input2":{"value":false}}`

In certain cases, payload contains lists (represented by `[]` delimiters). In this case, you have to specify either list index to use (starting with 1) or `*` in order to analyze all list items.

Previous examples detailed updates from MQTT to Domoticz devices. It's possible to push a change on Domoticz device to MQTT using the `set` tag:

```ts
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}, "retain": false},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    }
```

`topic` contains the topic to send the value to (defaults to primary topic if not specified). Set it to empty to ignore SET requests without error message.

`payload` contains the payload to send (defaults to `#`). The `#` character will be replaced by translated value (`Forced` in this example if Domoticz devices holds 20 in its level).

'retain' indicates if message should be sent with MQTT retain flag (default to true)

In some cases (in particular if device has to set boolean value, but not only), it may be necessary to have a different mapping between data read and data written. In this case, you can insert set mapping values that are different than those used to read. For example:

```
{
    "Kontor takbelysning": {
		"topic": "shellies/shellypro4pm-xxxx/status/switch:0",
		"type": "244", "subtype": "73", "switchtype": "0",
		"mapping": {
			"item": "output",
			"default": "0",
			"values": {"False": "0", "True" : "100"}
		},
		"set": {
			"topic": "shellies/shellypro4pm-xxxx/rpc",
			"payload": "{ \"id\":0, \"src\": \"domoticz\", \"method\": \"Switch.Set\", \"params\":{\"id\":0,\"on\":#}}",
			"mapping": {"values": {"false": "0", "true" : "100"}}
		}
     }
}
```

It's also possible to execute a bash command through `command` tag. In this case, unless you explicitly specify `topic`, no MQTT set will be send. Value to set will replace the `#`in command.

```ts
{
    "temp target heating": {
        "topic": "/home/alsavo/config/1",
        "type": "242", "subtype":"1","switchtype":0,
        "mapping":{"item":""},
         "set":{"command": "plugins/MqttMapper/test.sh #"}
    }
}
```

Note that bash command will be executed with a default folder equal to Domoticz root folder. Add `plugin/MqttMapper/` in command if you wish to execute commands into MqttMapper context. You may also specify a full path like `/home/user/...`.

If value to set is a float, lot of digits will be given to the command. A way to round it is to use `bc` command (`sudo apt install bc` if not already installed). Here's an example (replace `1` in `scale=1\ by number of digits you want so see after decimal point):

```ts
#!/bin/bash
value=$(echo "scale=1; $1 / 1" | bc)
echo "Received $value"
```

You may also use `'digit': n` in set command parameters to round value:

```ts
        "set": {"topic": "topic/xxx", "payload": {"value":"#"}, "digits": 2}
```

The previous `set` configuration is able to support simple commands as on/off or set level. For more complex ones, you may want to use specific topics and payloads. Here's an example of blinds, with open/close/stop and even percentage of opening:

```ts
"Test blind": {
	"topic": "blind/state",
	"type": "244", "subtype": "73", "switchtype": "21",
	"mapping": {"item": "value"},
	"commands": {
		"Open": {"topic": "blind/setOtherTopic", "payload": {"value": "Open"}},
		"Close": {"topic": "blind/setOtherTopic", "payload": {"value": "Close"}},
		"Stop": {"topic": "blind/setOtherTopic", "payload": {"value": "<command>"}},
		"Set Level":{"topic": "xxxx/setLevelTopic", "payload": "{\"value\": <level>}", "retain": true},
	}
}
```
Instead of `set` part, we have a `commands` part where we specify Domoticz commands (full list here under) we want to support, and give either topic and payload or shell command to execute.

In given example, `Open` and `Close` have fixed payload, `Stop` includes <command> value (here `Stop`), and `Set Level` has <level> value.

Level payload has a specific format, as numeric values are not allowed as string. Instead of putting directly JSON format in payload data, payload is put on a string, and quotes are escaped using "\".

Command list is not closed. You may want to add some as soon as you find them in Domoticz. However, here's list of discovered commands at time of writing this document: `On`, `Off`, `Toggle`, `Set Level`, `Open`, `Close`, `Stop`, `Set Color`. `<command>` contains the given command, `<level>` contains user requested level and `<color>` user requested color.

It's also possible to add a `<default>` command, that will be used if none of given commands matches those received. This could be the only command, if needed.

```ts
"commands": {
	"On": {"topic": "xxxx/setLevelTopic", "payload": {"value" : 100}},
	"Off": {"topic": "xxxx/setLevelTopic", "payload": {"value" : 0}},
	"<default>": {"topic": "xxxx/otherCommand", "payload": {"command": "<command>", "level": "<level>", "color": "<color>"}, "retain": true}
}
```

As already explained, it's also possible to specify a shell command instead of sending a MQTT message. Here's an example pushing all commands with their associated values to a script in MqttMapper plugin folder:

```ts
"commands": {
	"<default>": {"command": "plugins/MqttMapper/logCommand.sh \"<command>\" \"<level>\" \"<color>\""}
}
```

In some cases, MQTT update rate is higher than what we could/want expect. It's possible to rate limit messages to a certain level. This is done using the `throttle` keyword at device level, like :
```ts
    "Boiler power": {
        "topic": "boiler/SENSOR",
        "type": "248", "subtype": "1", "switchtype": "0",
		"throttle": 5,
        "mapping": {"item": "ENERGY/Power;ENERGY/Total"}}
    }
```

If a message is received while the previous change is less than `throttle` seconds, message will be saved (and overwritten by newer versions) until `throttle` is expired. At this time, Domoticz device will be updated. Messages are not lost, but only last version is kept, and updated every `throttle` seconds.

Note: to avoid tons of "Error: MQTT mapper hardware thread seems to have ended unexpectedly" in Domoticz logs, `throttle` can't be less than 3 seconds.

## Device options (partial) list

Here's a partial list of device options that can be specified in `options` of JSON configuration file.

| Device type    | Options                          | Meaning                                      |
|----------------|----------------------------------|----------------------------------------------|
| Counter        | `"ValueQuantity":"Distance",`    | `Distance` is label                          |
|                | `"ValueUnits":"km"`              | `km` is unit                                 |
| Custom counter | `1;km`                           | `1` is multiplier, `km` is unit              |
| Selector       | `"SelectorStyle":"1",`           | `0`=drop-down list, `1`= radio buttons       |
|                | `"LevelOffHidden": "true",`      | `true` to hide off level, `false` to show it |
|                | `"LevelNames":"Off|Auto|Forced"` | Labels of each level, separated by `|` (here `Off` = 0, `Auto` = 10, `Forced` = 20)|

## JSON files check

You may run checkJsonFiles.py to scan JSON file for important errors. It'll scan all JSON files in the current folder and display errors. Fix them until no errors are found.

## Debug tool

### dumpMqttMapper
To help debugging MqttMapper issues/configuration errors, a tool named dumpMqttMapperValues.py is available into plugin folder. It will scan plugin folder for configuration files, dump them with Domoticz API data, database content, and MQTT topics values. It will also check for device names duplicates, that often bring amazing side effects ;-) 

Cut and past output (or redirect it to a file) and send it to me. 

You can use the following options:
    [--input=<input file(s)>]: input file name (can be repeated, default to *.json.parameters). Can be used when multiple instances of plugin are run from the same folder.
    [--wait=<minutes>]: wait for MQTT changes for <minutes>. Can be used for topics not having a retain flag, to wait sufficient time to get an update.
    [--url=<domoticz URL>]: use this Domoticz URL instead of default http://127.0.0.1:8080/. You may specify username:password if needed. Don't forget http:// or https://.
    [--checkend]: check for device names sharing same text at end. In addition to identical device naming, this option allow checking devices ending by another device name.
    [--keep]: keep database copy and API response
    [--debug]: print debug messages
    [--help]: print this help message

To display all data, 2 Python extensions should be installed on the machine (the script can work without them, but will only display partial messages): paho-mqtt and sqlite3. If they're not installed, you'll get a warning message. You may install them using "pip3 install paho-mqtt" and "pip3 install sqlite3". If you have managed environment, replace these commands by "sudo apt install python3-paho-mqtt" and "sudo apt install python3-sqlite3".

### findDomoticzTypes

This tool allow to find information about types, subtypes and switch type, giving integer value (in decimal or hexa-decimal), or string (using a regular expression). It's even possible to get full list of supported combinations. It will display values, names, nValue and sValue(s) for each supported configuration.

# Examples
Here are some examples that may be useful. Each examples show (part of) setup file, content of topic used, Domoticz device value, and result description /

## Full topic content
```
Setup:
{"device": {"topic": "sensor/state",  "mapping": {"item": ""}}}

Topic content:
active since 1 hour

Domoticz device value:
[device] -> active since 1 hour
```

## One JSON item
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature"}}}

Topic content:
{"temperature": 19, "humidity":70}

Domoticz device value:
 19 
```

## With multiplier
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature",  "multiplier": 0.1}}}

Topic content:
{"temperature": 195, "humidity":700}

Domoticz device value:
19.5
```

## With mapping
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"}}}}

Topic content:
{"mode": "Auto"}

Domoticz device value:
 10 
```

## With default value
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"},  "default": "0"}}}

Topic content:
{"mode": "Unknown"}

Domoticz device value:
 0 
```

## With multiple items
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity"}}}

Topic content:
{"temperature": 19, "humidity":70}

Domoticz device value:
19;70
```

## With multiple items and constant
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity;~3"}}}

Topic content:
{"temperature": 19, "humidity":70}

Domoticz device value:
19;70;3
```

## One topic/Multiple devices
```
Setup:
{"device1":{"topic": "sensor/state", "key":"sensor/state-1", "mapping": {"item": "temperature"}},
"device2":{"topic": "sensor/state", "key":"sensor/state-2",  "mapping": {"item": "humitidy"}}}

Topic content:
{"temperature": 19, "humidity":70}

Domoticz device value:
[device1] ->  19
[device2] ->  70
```

## Item deeper in JSON message
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "sensor1/lastRead/temperature"}}}

Topic content:
{"sensor1": {"counter" : 123456, "lastRead" : {"temperature": 19, "humidity":70}}}

Domoticz device value:
 19 
```

## Item with list in JSON message
```
Setup:
{"device":{"topic": "gateway/12345/event/up", "mapping": {"item": "rxInfo/*/rssi"}}}

Topic Topic content:
{"rxInfo": [{"rssi": -69, "snr": 11.2, "channel": 2}]}

Domoticz device value:
 -69 
```

## Message with specific item value
```
Setup:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature"}, "select": {"item": "status", "value": "ok"}}

Topic content:
{"temperature": 19, "humidity":70, "status": "ok"}

Domoticz device value:
 19 

Topic content:
{"temperature": 19, "humidity":70, "status": "bad"}

-> Message ignored
 
```

------------------------------------------------

<a id="Version française"></a>
# Version française

MqttMapper est un plug-in Domoticz qui permet de relier des dispositifs Domoticz à MQTT directement.

## A quoi ça sert ?

Si vous voulez lire/écrire des sujets (topics) MQTT et les lier à des dispositifs Domoticz, sans avoir besoin d'installer NodeRed, et/ou intégrer des capteurs qui n'ont pas de découvertes HomeAssistant, ce plug-in est fait pour vous.

## Prérequis

- Domoticz 2022.0 ou supérieure (les versions précédentes peuvent aussi fonctionner)
- Vérifiez que votre version de Domoticz supporte les plug-ins Python (https://wiki.domoticz.com/Using_Python_plugins)

## Installation

Suivez ces étapes :

1. Clonez le dépôt GitHub dans le répertoire plug-ins de Domoticz
```
cd domoticz/plugins
git clone https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin.git MqttMapper
```
2. Redémarrer Domoticz 
3. Assurez-vous qu' "Acceptez les nouveaux dispositifs" est coché dans les paramètres de Domoticz
4. Allez dans la page "Matériel" du bouton "configuration" et ajouter une entrée de type "MqttMapper"
5. Entrez les informations de votre serveur MQTT dans les paramètres du plug-in (adresse, port, utilisateur, mot de passe)
6. entrez le nom du fichier de configuration JSON à utiliser (qui doit être dans le répertoire d'installation du plug-in MqttMapper)

## Mise à jour du plug-in

1. Allez dans le répertoire du plug-in et charger la nouvelle version
```
cd domoticz/plugins/MqttMapper
git pull
```
2. Relancez Domoticz

Note: si vous avez fait des modifs dans les fichiers du plug-in et que la commande `git pull` ne fonctionne pas, vous pouvez écraser les modifications locales avec la commande
```
git stash
```
ou
```
git checkout <fichier modifié>
```

## MQTT, qu’est-ce que c’est ?

MQTT est un système d’échange de messages basé sur des files d’attente permettant à des applications/serveurs d’envoyer (publier) des messages à d’autres applications/clients qui ont demandé à recevoir (souscrit à) ces messages.

Comme les clients peuvent ne pas être connectés lorsqu’on message est émis, le serveur peut ajouter un indicateur « retain » (retenu pu mémorisé) pour stocker la dernière version du message, qui sera envoyé lorsque les clients se connecteront.

Un grand nombre d’outils MQTT sont capables d’écrire et lire ces messages. Le client MQTT Explorer (https://mqtt-explorer.com/) est particulièrement connu. On peut être tenté d’en installer un pour voir ce qui se passe dans MQTT.

Les messages sont émis avec un nom (topic, traduit en français par sujet), par exemple "zigbee2mqtt/bridge/config". Dans MqttMapper, ceci correspond à "topic".

Les sujets pointent sur les données envoyées. Voici un exemple du sujet "zigbee2mqtt/bridge/config" :

```
{"commit":"56589dc","coordinator":{"meta":{"maintrel":1,"majorrel":2,"minorrel":7,"product":1,"revision":20220221,"transportrev":2},"type":"zStack3x0"},"log_level":"debug","network":{"channel":15,"extendedPanID":"0xeb344dd381129444","panID":22046},"permit_join":false,"version":"1.34.0"}
```

Comme on peut le voir, les données sont (très souvent) stockées au format JSON (mais on peut aussi trouver des données au format brut comme `20.5` ou `on`).

En utilisant des outils JSON (tels que l’extension JSON de NotePad++ ou l’extension JSON intégrée à MQTT Explorer), on peut obtenir une vision plus lisible comme :
```
{
	"commit": "56589dc",
	"coordinator": {
		"meta": {
			"maintrel": 1,
			"majorrel": 2,
			"minorrel": 7,
			"product": 1,
			"revision": 20220221,
			"transportrev": 2
		},
		"type": "zStack3x0"
	},
	"log_level": "debug",
	"network": {
		"channel": 15,
		"extendedPanID": "0xeb344dd381129444",
		"panID": 22046
	},
	"permit_join": false,
	"version": "1.34.0"
}
```
Pour accéder à la donnée `channel`  (15), on doit indiquer dans MqttMapper un `item` égal à  `network/channel` et à la donnée `revision` (20220221) égal à `coordinator/meta/revision`.

Quand la donnée n’est pas structurée (ou qu’on souhaite récupérer le message complet), on spécifie `"item": ""` dans MqttMapper.

En bref, utiliser un client MQTT pour avoir une vue de l’arborescence MQTT, trouver le sujet complet et le mettre dans `topic` dans MqttMapper, trouver la clef JSON des données et la mettre dans `item` (ou le laisser vide s’il n’est pas au format JSON).

Avec ça, on devrait avoir compris ces 2 concepts ;-)

## Configuration

Ce plug-in utilise un fichier de configuration externe au format JSON pour associer les topics MQTT avec les dispositifs Domoticz. Voici un exemple de syntaxe :
```ts
{
    "Car windows": {
        "topic": "volvo/xx-999-xx/binary_sensor/any_window_open/state",
        "type": "244", "subtype": "73", "switchtype": "11",
        "mapping": {"item": "", "default": "1", "values": {"close": "0"}}
    },
    "Car lock": {
        "topic": "volvo/xx-999-xx/lock/lock/state",
        "type": "244", "subtype": "73","switchtype": "11",
        "mapping": {"item": "", "default": "0", "values": {"lock": "1"}}
    },
    "Car engine running": {
        "topic": "volvo/xx-999-xx/binary_sensor/is_engine_running/state",
        "type": "244", "subtype": "73", "switchtype": "8", 
        "mapping": {"item": "", "default": "1", "values": {"off": "0"}
        }
    },
    "Car odometer": {"topic": "volvo/xx-999-xx/sensor/odometer/state",
        "type": "113", "subtype": "0", "switchtype": "3",
        "options": {"ValueQuantity":"Distance", "ValueUnits":"km"},
        "mapping": {"item": ""}
    },
    "Car fuel amount": {"topic": "volvo/xx-999-xx/sensor/fuel_amount/state",
        "type": "243", "subtype": "31", "switchtype": "0",
        "options": {"Custom":"1;L"},
        "mapping": {"item": ""}
    },
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
		"select": {"item": "isOk", "value": "yes"},
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    },
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0;0;0"},
        "mapping": {"item": "temperature;humidity;~0", "multiplier": "0.1;1;1", "digits": "1;0;0", "battery": "batLevel"}
    },
    "Boiler power": {
        "topic": "boiler/SENSOR",
        "type": "248", "subtype": "1", "switchtype": "0",
		"throttle": 5,
        "mapping": {"item": "ENERGY/Power;ENERGY/Total"}}
    },
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}, "retain": false},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    },
    "Kontor takbelysning": {
		"topic": "shellies/shellypro4pm-xxxx/status/switch:0",
		"type": "244", "subtype": "73", "switchtype": "0",
		"mapping": {
			"item": "output",
			"default": "0",
			"values": {"False": "0", "True" : "100"}
		},
		"set": {
			"topic": "shellies/shellypro4pm-xxxx/rpc",
			"payload": "{ \"id\":0, \"src\": \"domoticz\", \"method\": \"Switch.Set\", \"params\":{\"id\":0,\"on\":#}}",
			"mapping": {"values": {"false": "0", "true" : "100"}}
		}
     }?
	"Test blind": {
		"topic": "blind/state",
		"type": "244", "subtype": "73", "switchtype": "21",
		"mapping": {"item": "value"},
		"commands": {
			"Open": {"topic": "blind/setOtherTopic", "payload": {"value": "Open"}},
			"Close": {"topic": "blind/setOtherTopic", "payload": {"value": "Close"}},
			"Stop": {"topic": "blind/setOtherTopic", "payload": {"value": "<command>"}},
			"Set Level":{"topic": "xxxx/setLevelTopic", "payload": "{\"value\": <level>}", "retain": true},
		}
	}
}
```

Voyons comment c'est construit :

```ts
    "Car windows": {
        "topic": "volvo/xx-999-xx/binary_sensor/any_window_open/state",
        "type": "244", "subtype": "73", "switchtype": "11",
        "mapping": {"item": "", "default": "1", "values": {"close": "0"}}
    }

```

`Car windows` représente le nom du dispositif Domoticz à créer. `type`, `subtype` et `switchtype` contiennent les types/subtypes/switchtypes du dispositif à créer. La liste des valeurs supportées est disponible à (https://wiki.domoticz.com/Developing_a_Python_plugin#Available_Device_Types).

Vide ou égal à `~*`, `mapping` -> `item` indique que le contenu n'est pas dans un format JSON. La valeur extraite est le contenu de topic MQTT. La valeur par défaut est indiquée dans `default` et les valeurs associées sont dans `values` . Dans cet exemple, lorsque le contenu est `close`, le dispositif est mis à `1`.

En gros, quand un topic `volvo/xx-999-xx/binary_sensor/any_window_open/state` contient la valeur `close`, un interrupteur `(244/73/11)` est mis à fermé, ouvert sinon.

Lorsque `default` n'est pas spécifié, la valeur extraite est directement chargée dans le dispositif associé.

```ts
    "Car odometer": {"topic": "volvo/xx-999-xx/sensor/odometer/state",
        "type": "113", "subtype": "0", "switchtype": "3",
        "options": {"ValueQuantity":"Distance", "ValueUnits":"km"},
        "mapping": {"item": ""}
    }
```

Dans cet exemple, `options` contient les options utilisées pour créer le dispositif. Je n'ai malheureusement pas trouvé de liste complète, j'ai mis une ébauche à la fin de ce document.

```ts
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
		"select": {"item": "isOk", "value": "yes"},
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    }
```

Cette fois, le contenu est au format JSON (`item` n'est pas vide). La valeur extraite sera prise dans l'item `temperature` du contenu, au niveau supérieur. `ENERGY/Power` dans l'exemple suivant indique que la valeur sera extraite de l'item `Power` de l'item `Energy`.

`multiplier` est optionnel et indique le facteur à appliquer à la valeur numérique (ici `0.1`, équivalent à diviser par 10). Lorsque vous avez plusieurs multiplicateurs à indiquer,, vous pouvez les spécifier comme "0.1;10;1"
'digits' est également optionnel et indique le nombre de décimales à utiliser pour arrondir la valeur. Là encore, vous pouvez utiliser "1;2;0" si vous avez plusieurs valeurs à donner.

`select` permet de ne considérer que les messages ayant un item particulier contenant une valeur spécifique (sinon, le message sera simplement ignoré). Ici, seuls les messages avec `"isOk": "yes"` seront sélectionnés.

```ts
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0;0;0"},
        "mapping": {"item": "temperature;humidity;~0", "multiplier": "0.1;1;1", "digits": "1;0;0", "battery": "batLevel"}
    }
```

Pour indiquer des valeurs multiples, séparez-les par des `;`, comme dans `temperature;humidity`. La valeur chargée sera la concaténation des deux items.

Noter que vous pouvez aussi insérer des constantes, en les préfixant par `~`. Par exemple `total;~0;~0;~0;power;~0` pour spécifier le contenu de type sValue d'un compteur en KWh.

Si vous voulez ne changer qu'une partie de la variable sValue d'un dispositif, vous pouvez utiliser `~` seul pour conserver une partie existante. Par exemple, `value;~` va insérer le contenu de l'item value et conserver la seconde partie de sValue.

Pour définir une valeur initiale pour nvalue ou svalue sur un dispositif, vous pouvez utiliser "initial": {"nvalue": 123} ou "initial": {"svalue": "abc"} ou les deux.

Vous pouvez aussi utiliser "battery" suivi du nom extrait du contenu JSON (ici "batLevel"), de la même façon qu'"item"

Vous pouvez avoir besoin de créer plusieurs dispositifs à partir d'un même topic. Dans ce cas, utilisez l'item optionnel `key` pour spécifier un clef "virtuelle". Cette clef peut être n'importe quoi, tant qu'elle est unique et différente des topics utilisés. Par exemple :
```ts
{
     "mvtdec1": {
        "topic": "KC868_AI/1234567890/STATE",
        "key": "KC868_AI/1234567890/STATE-input1",
        "type": "244", "subtype": "73", "switchtype": "8",
        "mapping": {"item": "input1/value", "default": "0", "values": {"True": "1"}}
    },
     "mvtdec2": {
        "topic": "KC868_AI/1234567890/STATE",
        "key": "KC868_AI/1234567890/STATE-input2",
        "type": "244", "subtype": "73", "switchtype": "8",
        "mapping": {"item": "input2/value", "default": "0", "values": {"True": "1"}}
    }
}
```
va décoder proprement un message json comme `{"input1":{"value":false},"input2":{"value":false}}`

Dans certains cas, la charge contient une liste (représentée par les délimiteurs `[]`). Dans ce cas, vous devez spécifier soit l'index de la liste à utiliser (démarrant à 1), soit `*`pour analyser l'ensemble des éléments de la liste.

Les exemples précédents détaillaient des mises à jour depuis MQTT vers des dispositifs Domoticz. Il est également possible de pousser un changement initié par Domoticz vers MQTT en utilisant le mot clef `set` :

```ts
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}, "retain": false},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    }
```

`topic` contient le topic vers lequel la valeur sera envoyée (par défaut, on utilisera celui du dispositif). Mettez le vide pour ignorer les demandes de modification sans afficher d'erreur. 

`payload` contient la valeur à envoyer (par défaut `#`). Le caractère `#` sera remplacé par la valeur associée (Dans cet exemple, `Forced` si le dispositif Domoticz contient un niveau 20).

'retain' indique si le message doit être envoyé avec le flag MQTT retain (par défaut: true), et donc mémorisé.

Dans certains cas (en particulier si le dispositif utilise des valeurs booléennes, mais pas que), il peut être nécessaire d'utiliser une association différente de celle de la lecture lors de l'écriture . Par exemple :

```
{
    "Kontor takbelysning": {
		"topic": "shellies/shellypro4pm-xxxx/status/switch:0",
		"type": "244", "subtype": "73", "switchtype": "0",
		"mapping": {
			"item": "output",
			"default": "0",
			"values": {"False": "0", "True" : "100"}
		},
		"set": {
			"topic": "shellies/shellypro4pm-xxxx/rpc",
			"payload": "{ \"id\":0, \"src\": \"domoticz\", \"method\": \"Switch.Set\", \"params\":{\"id\":0,\"on\":#}}",
			"mapping": {"values": {"false": "0", "true" : "100"}}
		}
     }
}
```

Il est également possible d'exécuter une commande bash avec le tag `command`. Dans ce cas, il n'y aura pas de set MQTT, sauf si vous spécifiez explicitement le tag `topic`. Les `#` présents dans la commande seront remplacés par la valeur à affecter.

```ts
{
    "temp target heating": {
        "topic": "/home/alsavo/config/1",
        "type": "242", "subtype":"1","switchtype":0,
        "mapping":{"item":""},
         "set":{"command": "plugins/MqttMapper/test.sh #"}
    }
}
```

Noter que la commande bash sera exécutée par défaut dans le répertoire de Domoticz. Ajoutez `plugin/MqttMapper/`  dans la commande si vous souhaitez l'exécuter dans le contexte de MqttMapper. Vous pouvez aussi spécifier un chemin complet comme `/home/user/...`.

Si la valeur à définir est un nombre flottant, de nombreuses décimales seront passées à la commande. Une façon de l'arrondir est d'utiliser la commande `bc` (à installer par `sudo apt install bc` si elle n'existe pas). Voici un exemple (remplacer `1` dans  `scale=1\ par le nombre de décimales souhaitées) :

```ts
#!/bin/bash
value=$(echo "scale=1; $1 / 1" | bc)
echo "Received $value"
```

Vous pouvez aussi utiliser `'digit': n` dans les paramètres de la commande set pour arrondir la valeur:

```ts
        "set": {"topic": "topic/xxx", "payload": {"value":"#"}, "digits": 2}
```

Les exemples précédents d'utilisation de `set` peuvent supporter des commandes simples, telles que marche/arrêt ou intensité. Pour les cas plus complexes, vous pouvez souhaiter utiliser des sujet ou des contenus spécifiques. Voici un exemple de volet, avec ouverture/fermeture/arrêt et même pourcentage d'ouverture:

```ts
"Test blind": {
	"topic": "blind/state",
	"type": "244", "subtype": "73", "switchtype": "21",
	"mapping": {"item": "value"},
	"commands": {
		"Open": {"topic": "blind/setOtherTopic", "payload": {"value": "Open"}},
		"Close": {"topic": "blind/setOtherTopic", "payload": {"value": "Close"}},
		"Stop": {"topic": "blind/setOtherTopic", "payload": {"value": "<command>"}},
		"Set Level":{"topic": "xxxx/setLevelTopic", "payload": "{\"value\": <level>}", "retain": true},
	}
}
```
Au lieu d'une partie `set`, on a ici une partie `commands` où on peut indiquer les commandes Domoticz gérées (voir la liste complète ci-dessous), et donner soit les sujets et contenus, soit les commandes systèmes ) passer.

Dans l'exemple donné, `Open` et `Close` ont un contenu fixe, `Stop` inclue la valeur <command> (ici `Stop`), et `Set Level` a la valeur <level>.

Le contenu de payload a un format spécifique, les valeurs numériques n'étant pas autorisées dans des chaînes de caractères. Au lieu d'indiquer directement du JSON dans le contenu, la charge est mise dans une chaîne de caractères et les marques "guillemets" sont échappées par un "\".

La liste des commandes n'est pas fixe. On peut en ajouter dès que Domoticz en ajoute. Pour aider, voici la liste des commandes découvertes dans Domoticz au moment de l'écriture de ce document : `On`, `Off`, `Toggle`, `Set Level`, `Open`, `Close`, `Stop`, `Set Color`. `<command>` contient la commande passée par Domoticz, `<level>` contient l'intensité ou le niveau donné par l'utilisateur et `<color>` la couleur donnée par l'utilisateur.

Il est également possible d'indiquer une commande `<default>` qui sera utilisée si aucune des commandes données ne correspondant à celle reçue. Ce peut être la seule, si besoin.

```ts
"commands": {
	"On": {"topic": "xxxx/setLevelTopic", "payload": {"value" : 100}},
	"Off": {"topic": "xxxx/setLevelTopic", "payload": {"value" : 0}},
	"<default>": {"topic": "xxxx/otherCommand", "payload": {"command": "<command>", "level": "<level>", "color": "<color>"}, "retain": true}
}
```

Comme expliqué plus haut, il est également possible d'exécuter une commande système au lieu d'envoyer un message MQTT. Voici un exemple qui envoie toutes les commandes à un script dans le répertoire du plugin MqttMapper:

```ts
"commands": {
	"<default>": {"command": "plugins/MqttMapper/logCommand.sh \"<command>\" \"<level>\" \"<color>\""}
}
```

Dans certains cas, l'intervalle de mise à jour des messages MQTT est plus élevé que ce qu'on souhaite. Il est possible de limiter le débit de mise à jour d'un dispositif en ajoutant le mot clef `throttle` au niveau du dispositif, comme ça :
```ts
    "Boiler power": {
        "topic": "boiler/SENSOR",
        "type": "248", "subtype": "1", "switchtype": "0",
		"throttle": 5,
        "mapping": {"item": "ENERGY/Power;ENERGY/Total"}}
    }
```

Si un message est reçu alors que le délai avec la dernière modification du dispositif est inférieur à `throttle` secondes, le message sera sauvegardé (et écrase par de nouvelles versions si besoin) jusqu'à ce que le délai `throttle` expire. A ce moment, le dispositif Domoticz  sera mis à jour avec la dernière version. Les messages ne sont pas perdus, mais seule la dernière version est conservée et mise à jour toutes les `throttle` secondes.

Note: pour éviter de récupérer des tonnes de "Error: MQTT mapper hardware thread seems to have ended unexpectedly" dans les logs de Domoticz, `throttle` doit être au moins égal à 3 secondes.

## Liste (partielle) des options

Voici une liste partielle des options utilisables avec le mot clef `options` du fichier de configuration au format JSON.

| Dispositif     | Options                          | Signification                               |
|----------------|----------------------------------|---------------------------------------------|
| Counter        | `"ValueQuantity":"Distance",`    | `Distance` est utilisé comme étiquette      |
|                | `"ValueUnits":"km"`              | `km` représente l'unité                     |
| Custom counter | `1;km`                           | `1` est le multiplicateur, `km` l'unité     |
| Selector       | `"SelectorStyle":"1",`           | `0` = liste déroulante, `1` = boutons radio |
|                | `"LevelOffHidden": "true",`      | `true` pour cacher le niveau off, `false` pour le montrer |
|                | `"LevelNames":"Off|Auto|Forced"` | Etiquettes de chaque niveau, séparées par `|` (ici `Off` = 0, `Auto` = 10, `Forced` = 20)|

## Vérification des fichiers JSON

Vous pouvez vérifier les erreurs les plus flagrantes des fichiers JSON avec le script checkJsonFiles.py. Il va scanner l'ensemble des .JSON présents dans le répertoire courant et afficher les erreurs. Corrigez jusqu'à ce qu'aucune erreur ne soit affichée.

## Outil de déverminage

### dumpMqttMapper

Pour aider au déverminage des problèmes de MQTTMapper ou des fichiers de configuration, un script nommé dumpMqttMapperValues.py est disponible dans le répertoire du plugin. Il va chercher les fichiers de configuration dans le répertoire courant, afficher leur contenu, les données de l'API Domoticz et de la base de données, ainsi que les topics MQTT associés sur l'écran. Il détecte aussi les noms de dispositifs dupliqués, qui apportent des effets de bord aussi amusants qu'inattendus ;-)

Copiez/collez (ou redirigez) les messages pour me les envoyer.

Les options suivantes sont disponibles :
    [--input=<Fichier(s) a analyser>]: fichier(s) en entrée (peut être répété, par défaut on utilise *.json.parameters). Peut être utilisé lorsque plusieurs instances du plugin sont lancées depuis le même répertoire.
    [--wait=<minutes>]: attend les changements des topics pendant <minutes>. Peut être utilisé pour les topics qui n'ont pas l'indicateur "retain", pour attendre un changement suffisamment longtemps.
    [--url=<URL de Domoticz>]: utiliser cette URL Domoticz au lieu du défaut http://127.0.0.1:8080/. Vous pouvez spécifier si besoin username:password. N'oubliez pas http:// ou https://.
    [--checkend]: vérifie les dispositifs partageant la même fin de nom. En plus des dispositifs possédant le même nom, cette option permet de détecter les mêmes terminaisons.
    [--keep]: conserve la copie de la base et la réponse de l'API
    [--debug]: affiche les messages de déverminage
    [--help]: affiche ce message d'aide (en version anglaise)

Pour afficher l'ensemble des données, 2 extensions Python peuvent être installées sur la machine (le script peut fonctionner sans elles, mais seules des informations partielles seront affichées). Si elles ne sont pas installées, vous aurez un message. Vous pouvez les installer en utilisant les commandes "pip3 install paho-mqtt" et "pip3 install sqlite3". Si vous avez un environnement managé, remplacez ces commandes par "sudo apt install python3-paho-mqtt" et "sudo apt install python3-sqlite3".

### findDomoticzTypes

Cet outil permet de trouver des informations sur les types, subtypes et switchtypes, à partir d'une valeur décimale, hexa-décimale ou chaîne de caractères (en utilisation une expression régulière) Il est même possible d'obtenir la liste des combinaisons supportées. Les valeurs, noms, nValue et sValue(s) pour chaque configuration supportées.

# Exemples
Vous trouverez ci-dessous des exemples utiles. Chaque exemple montre (une partie de) la configuration, le contenu du topic utilisé, la valeur du dispositif Domoticz et la description du résultat

## Totalité du contenu du topic
```
Configuration :
{"device": {"topic": "sensor/state",  "mapping": {"item": ""}}}

Contenu du topic :
active since 1 hour

Valeur du dispositif Domoticz :
[device] -> active since 1 hour
```

## Un item du message JSON
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature"}}}

Contenu du topic :
{"temperature": 19, "humidity":70}

Valeur du dispositif Domoticz :
 19 
```

## Avec Multiplicateur
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature",  "multiplier": 0.1}}}

Contenu du topic :
{"temperature": 195, "humidity":700}

Valeur du dispositif Domoticz :
19.5
```

## Avec association
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"}}}}

Contenu du topic :
{"mode": "Auto"}

Valeur du dispositif Domoticz :
 10 
```

## Avec valeur par défaut
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"},  "default": "0"}}}

Contenu du topic :
{"mode": "Unknown"}

Valeur du dispositif Domoticz :
 0 
```

## Avec plusieurs items
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity"}}}

Contenu du topic :
{"temperature": 19, "humidity":70}

Valeur du dispositif Domoticz :
19;70
```

## Avec plusieurs items et constante
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity;~3"}}}

Contenu du topic :
{"temperature": 19, "humidity":70}

Valeur du dispositif Domoticz :
19;70;3
```

## Un topic/Plusieurs dispositifs
```
Configuration :
{"device1":{"topic": "sensor/state", "key":"sensor/state-1", "mapping": {"item": "temperature"}},
"device2":{"topic": "sensor/state", "key":"sensor/state-2",  "mapping": {"item": "humitidy"}}}

Contenu du topic :
{"temperature": 19, "humidity":70}

Valeur du dispositif Domoticz :
[device1] ->  19
[device2] ->  70
```

## L'item est enfoui dans le message JSON
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "sensor1/lastRead/temperature"}}}

Contenu du topic :
{"sensor1": {"counter" : 123456, "lastRead" : {"temperature": 19, "humidity":70}}}

Valeur du dispositif Domoticz :
 19 
```

## L'item est dans une liste du message JSON
```
Configuration :
{"device":{"topic": "gateway/12345/event/up", "mapping": {"item": "rxInfo/*/rssi"}}}

Contenu du topic :
{"rxInfo": [{"rssi": -69, "snr": 11.2, "channel": 2}]}

Valeur du dispositif Domoticz :
 -69 
```

## Messages avec une valeur particulière
```
Configuration :
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature"}, "select": {"item": "status", "value": "ok"}}

Contenu du topic :
{"temperature": 19, "humidity":70, "status": "ok"}

Valeur du dispositif Domoticz :
 19 

Contenu du topic :
{"temperature": 19, "humidity":70, "status": "bad"}

-> Message ignoré
 
```
