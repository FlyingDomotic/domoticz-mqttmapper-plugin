# MqttMapper Domoticz plugin

MqttMapper is a Domoticz Python plugin allowing to map MQTT topics directly to Domoticz devices.

## What's for?
If you want to be able to read some MQTT topics and maps them to Domoticz devices, without having to install NodeRed, and integrate sensors that don't have HomeAssistant discovery item, this plugin is made for you.

## Warning

This plugin is at an early stage, and has only partly be tested, with few Domoticz devices types. In addition, bad JSON configuration files will lead to unexpected behavior. You've been warned!

## Prerequisites

- Domoticz 2020.0 or higher (but lower version could also work)
- Make sure that your Domoticz supports Python plugins (https://www.domoticz.com/wiki/Using_Python_plugins)

## Installation

Follow these steps:

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin.git MqttMapper
```
2. Restart domoticz
3. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
4. Go to "Hardware" page and add new item with type "MqttMapper"
5. Set your MQTT server information to plugin settings (address, port, username, password)
6. Give JSON configuration file name to be used (located in plugin folder)

## Plugin update

1. Go to plugin folder and pull new version
```
cd domoticz/plugins/MqttMapper
git pull
```
2. Restart domoticz

Note: if you did any changes to plugin files and `git pull` command doesn't work for you anymore, you could stash all local changes using
```
git stash
```

## Configuration

Plugin uses an external JSON configuration file to map MQTT topics to Domoticz devices. Here's an example of syntax:

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
        "mapping": {"item": "temperature"}
    },
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "mapping": {"item": "temperature;humidity"}
    },
    "Boiler power": {
        "topic": "boiler/SENSOR",
        "type": "248", "subtype": "1", "switchtype": "0",
        "mapping": {"item": "ENERGY/Power;ENERGY/Total"}}
    },
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
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

`Car windows` is the name of Domoticz device to be created. `type`, `subtype` and `switchtype` contains the type/subtype/switchtype values of device being created. Valid values can be found at (https://www.domoticz.com/wiki/Developing_a_Python_plugin#Available_Device_Types).

When empty, `mapping` -> `item` indicates that payload is not in a JSON format. Extracted value is content of paylod. Default value is set in `default` and mapping values in `values` . Here, when payload is `close`, device is set to `1`.

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
        "mapping": {"item": "temperature"}
    }
```

This time, payload is in JSON format (`item` is not empty). This mean that the value will be extracted from `temperature` payload item, at the root level. `ENERGY/Power` in later example means that value will be extrated in `Power`item of `Energy` root item.

```ts
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "mapping": {"item": "temperature;humidity"}
    }
```

To specify multiple values, separate them with a `;`, like in `temperature;humidity`. Device value will be set with the concatenation of the two items.

Note that you also can specify constants in the list, prefixing them with `~`. For example `total;~0;~0;~0;power;~0`to generate a kw counter sValue.

Previous examples detailled updates from MQTT to Domoticz devices. It's possible to push a change on Domoticz device to MQTT using the `set` tag:

```ts
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    }
```

`topic` contains the topic to send the value to (defaults to primary topic if not specified).
`payload` contains the payload to send (defaults to `#`). The `#` character will be replaced by translated value (`Forced`in thi example if Domoticz devices holds 20 in its level).

## Device options (partial) list

Here's a partial list of device options that can be specified in `options` of JSON configuration file.

| Device type    | Options                          | Meaning                                     |
|----------------|----------------------------------|---------------------------------------------|
| Counter        | `"ValueQuantity":"Distance",`    | `Distance`is label                          |
|                | `"ValueUnits":"km"`              | `km`is unit                                 |
| Custom counter | `1;km`                           | `1` is multiplier, `km` is unit             |
| Selector       | `"SelectorStyle":"1",`           | `0`for dropdown list, `1`for radio buttons  |
|                | `"LevelOffHidden": "true",`      | `true` to hide off level, `false`to show it |
|                | `"LevelNames":"Off|Auto|Forced"` | Labels of each level, separated by `|` (here `Off` = 0, `Auto` = 10, `Forced` = 20)|