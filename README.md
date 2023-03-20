# MqttMapper Domoticz plugin / Plugin MqttMapper pour Domoticz

[English version and French version in the same document]

MqttMapper is a Domoticz Python plugin allowing to map MQTT topics directly to Domoticz devices.

[ Versions françaises et anglaises dans le même document]

MqttMapper est un plugin Domoticz qui permet de relier des dispositifs Domoticz à MQTT directement.

## What's for? / A quoi ça sert ?
If you want to be able to read/write some MQTT topics and maps them to Domoticz devices, without having to install NodeRed, and integrate sensors that don't have HomeAssistant discovery item, this plugin is made for you.

Si vous voulez lire/écrire des topics MQTT et les lier à des dispositifs Domoticz, sans avoir besoin d'installer NodeRed, et intégrer des capteurs qui n'ont pas de découvertes HomeAssistant, ce plugin est fait pour vous.

## Warning / Attention

This plugin is at an early stage, and has only partly be tested, with few Domoticz devices types. In addition, bad JSON configuration files will lead to unexpected behavior. You've been warned!

Ce plugin est en phase de développement initial, et n'a été que partiellement testé, avec seulement certains types de dispositifs Domoticz. De plus, un fichier de configuration JSON incorrect va provoquer des effets inattendus, voire rigolos. Vous avez été prévenus !

## Prerequisites / Prérequis

- Domoticz 2020.0 or higher (but lower version could also work)
- Make sure that your Domoticz supports Python plugins (https://www.domoticz.com/wiki/Using_Python_plugins)

- Domoticz 2022.0 ou supérieurs (les versions précédentes peuvent aussi fonctionner)
- Vérifiez que votre version de Domoticz supporte les plugins Python (https://www.domoticz.com/wiki/Using_Python_plugins)

## Installation

Follow these steps:

1. Clone repository into your Domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin.git MqttMapper
```
2. Restart Domoticz
3. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
4. Go to "Hardware" page and add new item with type "MqttMapper"
5. Set your MQTT server information to plugin settings (address, port, username, password)
6. Give JSON configuration file name to be used (located in MqttMapper plugin folder)

Suivez ces étapes :

1. Clonez le dépôt GitHub dans le répertoire plugins de Domoticz
```
cd domoticz/plugins
git clone https://github.com/FlyingDomotic/domoticz-mqttmapper-plugin.git MqttMapper
```
2. Redémarrer Domoticz 
3. Assurez-vous qu' "Acceptez les nouveaux dispositifs" est coché dans les paramètres de Domoticz
4. Allez dans la page "Matériel" du bouton "configuration" et ajouter une entrée de type "MqttMapper"
5. Entrez les informations de votre serveur MQTT dans les paramètres du plugin (adresse, port, utilisateur, mot de passe)
6. entrez le nom du fichier de configuration JSON à utiliser (qui doit être dans le répertoire d'installation du plugin MqttMapper)

## Plugin update / Mise à jour du plugin

1. Go to plugin folder and pull new version
```
cd domoticz/plugins/MqttMapper
git pull
```
2. Restart Domoticz

Note: if you did any changes to plugin files and `git pull` command doesn't work for you anymore, you could stash all local changes using
```
git stash
```
or
```
git checkout <modified file>
```

1. Allez dans le répertoire du plugin et charger la nouvelle version
```
cd domoticz/plugins/MqttMapper
git pull
```
ou
```
git checkout <fichier modifié>
```
2. Relancez Domoticz

Note: si vous avez fait des modifs dans les fichiers du plugin et que la commande `git pull` ne fonctionne pas, vous pouvez écraser les modifications locales avec la commande
```
git stash
```

## Configuration

Plugin uses an external JSON configuration file to map MQTT topics to Domoticz devices. Here's an example of syntax:

Ce plugin utilise un fichier de configuration externe au format JSON pour associer les topics MQTT avec les dispositifs Domoticz. Voici un exemple de syntaxe :
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
        "mapping": {"item": "temperature", "multiplier": 0.1}
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

Let's see how this is constructed: / Voyons comment c'est construit :

```ts
    "Car windows": {
        "topic": "volvo/xx-999-xx/binary_sensor/any_window_open/state",
        "type": "244", "subtype": "73", "switchtype": "11",
        "mapping": {"item": "", "default": "1", "values": {"close": "0"}}
    }

```

`Car windows` is the name of Domoticz device to be created. `type`, `subtype` and `switchtype` contains the type/subtype/switchtype values of device being created. Valid values can be found at (https://www.domoticz.com/wiki/Developing_a_Python_plugin#Available_Device_Types).

When empty, `mapping` -> `item` indicates that payload is not in a JSON format. Extracted value is content of payload. Default value is set in `default` and mapping values in `values`. Here, when payload is `close`, device is set to `1`.

In short, when receiving topic `volvo/xx-999-xx/binary_sensor/any_window_open/state` with value `close`, a switch device `(244/73/11)` is set to off, else on.

When `default` is not specified, the extracted value will be directly loaded in associated device.

`Car windows` représente le nom du dispositif Domoticz à créer. `type`, `subtype` et `switchtype` contiennent les types/subtypes/switchtypes du dispositif à créer. La liste des valeurs supportées est disponible à (https://www.domoticz.com/wiki/Developing_a_Python_plugin#Available_Device_Types).

Vide, `mapping` -> `item` indique que le contenu n'est pas dans un format JSON. La valeur extraite est le contenu de topic MQTT. La valeur par défaut est indiquée dans `default` et les valeurs associées sont dans `values` . Dans cet exemple, lorsque le contenu est `close`, le dispositif est mis à `1`.

En gros, quand un topic `volvo/xx-999-xx/binary_sensor/any_window_open/state` contient la valeur `close`, un interrupteur `(244/73/11)` est mis à fermé, ouvert sinon.

Lorsque `default` n'est pas spécifié, la valeur extraite est directement chargée dans le dispositif associé.

```ts
    "Car odometer": {"topic": "volvo/xx-999-xx/sensor/odometer/state",
        "type": "113", "subtype": "0", "switchtype": "3",
        "options": {"ValueQuantity":"Distance", "ValueUnits":"km"},
        "mapping": {"item": ""}
    }
```

Here, `options` contains the options used to create the device. Obviously, I don't find a full list, I put a partial one at end of this document. 

Dans cet exemple, `options` contient les options utilisées pour créer le dispositif. Je n'ai malheureusement pas trouvé de liste complète, j'ai mis une ébauche à la fin de ce document.

```ts
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
        "mapping": {"item": "temperature", "multiplier": 0.1}
    }
```

This time, payload is in JSON format (`item` is not empty). This mean that the value will be extracted from `temperature` payload item, at the root level. `ENERGY/Power` in later example means that value will be extracted in `Power` item of `Energy` root item.

`multiplier` is optional, and gives the factor to apply to numeric value (here `0.1`, equivalent to divid by 10).

Cette fois, le contenu est au format JSON (`item` n'est pas vide). La valeur extraite sera prise dans l'item `temperature` du contenu, au niveau supérieur. `ENERGY/Power` dans l'exemple suivant indique que la valeur sera extraite de l'item `Power` de l'item `Energy`.

`multiplier` est optionnel et indique le facteur à appliquer à la valeur numérique (ici `0.1`, équivalent à diviser par 10).

```ts
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "mapping": {"item": "temperature;humidity"}
    }
```

To specify multiple values, separate them with a `;`, like in `temperature;humidity`. Device value will be set with the concatenation of the two items.

Note that you also can specify constants in the list, prefixing them with `~`. For example `total;~0;~0;~0;power;~0` to generate a kWh counter sValue.

Should you want to change only part of sValue, you may use `~` alone to keep current value. For example, `value;~` will insert content of value item and keep second part of sValue.

The following example will load a KWh counter with elements from tow different topics:

Pour indiquer des valeurs multiples, séparez-les par des `;`, comme dans `temperature;humidity`. La valeur chargée sera la concaténation des deux items.

Noter que vous pouvez aussi insérer des constantes, en les préfixant par `~`. Par exemple `total;~0;~0;~0;power;~0` pour spécifier le contenu de type sValue d'un compteur en KWh.

Si vous voulez ne changer qu'une partie de la variable sValue d'un dispositif, vous pouvez utiliser `~` seul pour conserver une partie existante. Par exemple, `value;~` va insérer le contenu de l'item value et conserver la seconde partie de sValue.

L'exemple suivant permet de charger un compteur de type KWh avec des éléments de deux topics différents :

```
      "My KWh counter" : {
        "topic": "plug/power",
        "key": "My KWh counter",
        "type": "248", "subtype": "1", "switchtype": "0",
        "mapping": {"item": "val;~"}
      },
      "My KWh counter2" : {
        "topic": "plug/counter",
        "key": "My KWh counter",
        "type": "248", "subtype": "1", "switchtype": "0",
        "mapping": {"item": "~;val"}
      }
```

You may need to create multiple devices from the same topic. In this case, use optional `key` item to specify a "virtual" key. This key can be anything, as long as it is unique and different from topics. For exemple:

Vous pouvez avoir besoin de créer plusieurs dispositifs à partir d'un même topic. Dans ce cas, utilisez l'item optionnel `key` pour spécifier un clef "virtuelle". Cette clef peut être n'importe quoi, tant qu'elle est unique et différente des topics utilisés. Par exemple :
```
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
will map properly a json payload as / va décoder proprement un message json comme `{"input1":{"value":false},"input2":{"value":false}}`

Previous examples detailed updates from MQTT to Domoticz devices. It's possible to push a change on Domoticz device to MQTT using the `set` tag:

Les exemples précédents détaillaient des mises à jour depuis MQTT vers des dispositifs Domoticz. Il est également possible de pousser un changement initié par Domoticz vers MQTT en utilisant le mot clef `set` :

```ts
    "Mode selector": {"topic": "fan/mode",
        "type": "244", "subtype": "62", "switchtype": "18",
        "options": {"SelectorStyle":"1", "LevelOffHidden": "true", "LevelNames":"Off|Auto|Forced"},
        "set": {"topic": "fan/mode/set", "payload": {"mode":"#"}},
        "mapping": {"item": "mode", "default": "0", "values": {"Off": "0", "Auto": "10", "Forced": "20"}}
    }
```

`topic` contains the topic to send the value to (defaults to primary topic if not specified).
`payload` contains the payload to send (defaults to `#`). The `#` character will be replaced by translated value (`Forced` in this example if Domoticz devices holds 20 in its level).

`topic` contient le topic vers lequel la valeur sera envoyée (par défaut, on utilisera celui du dispositif).

`payload` contient la valeur à envoyer (par défaut `#`). Le caractère `#` sera remplacé par la valeur associée (Dans cet exemple, `Forced` si le dispositif Domoticz contient un niveau 20).

## Device options (partial) list / Liste (partielle) des options

Here's a partial list of device options that can be specified in `options` of JSON configuration file.

| Device type    | Options                          | Meaning                                      |
|----------------|----------------------------------|----------------------------------------------|
| Counter        | `"ValueQuantity":"Distance",`    | `Distance` is label                          |
|                | `"ValueUnits":"km"`              | `km` is unit                                 |
| Custom counter | `1;km`                           | `1` is multiplier, `km` is unit              |
| Selector       | `"SelectorStyle":"1",`           | `0` for dropdown list, `1` for radio buttons |
|                | `"LevelOffHidden": "true",`      | `true` to hide off level, `false` to show it |
|                | `"LevelNames":"Off|Auto|Forced"` | Labels of each level, separated by `|` (here `Off` = 0, `Auto` = 10, `Forced` = 20)|

Voici une liste partielle des options utilisables avec le mot clef `options` du fichier de configuration au format JSON.

| Dispositif     | Options                          | Signification                               |
|----------------|----------------------------------|---------------------------------------------|
| Counter        | `"ValueQuantity":"Distance",`    | `Distance` est utilisé comme étiquette      |
|                | `"ValueUnits":"km"`              | `km` représente l'unité                     |
| Custom counter | `1;km`                           | `1` est le multiplicateur, `km` l'unité     |
| Selector       | `"SelectorStyle":"1",`           | `0` = liste déroulante, `1` = boutons radio |
|                | `"LevelOffHidden": "true",`      | `true` pour cacher le niveau off, `false` pour le montrer |
|                | `"LevelNames":"Off|Auto|Forced"` | Etiquettes de chaque niveau, séparées par `|` (ici `Off` = 0, `Auto` = 10, `Forced` = 20)|
