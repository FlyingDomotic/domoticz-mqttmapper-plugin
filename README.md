# MqttMapper Domoticz plug-in / plug-in MqttMapper pour Domoticz

[English version and French version in the same document]

MqttMapper is a Domoticz Python plug-in allowing to map MQTT topics directly to Domoticz devices.

[ Versions françaises et anglaises dans le même document]

MqttMapper est un plug-in Domoticz qui permet de relier des dispositifs Domoticz à MQTT directement.

## What's for? / A quoi ça sert ?
If you want to be able to read/write some MQTT topics and maps them to Domoticz devices, without having to install NodeRed, and/or integrate sensors that don't have HomeAssistant discovery item, this plug-in is made for you.

Si vous voulez lire/écrire des topics MQTT et les lier à des dispositifs Domoticz, sans avoir besoin d'installer NodeRed, et/ou intégrer des capteurs qui n'ont pas de découvertes HomeAssistant, ce plug-in est fait pour vous.

## Warning / Attention

This plug-in is at an early stage, and has only partly be tested, with few Domoticz devices types. In addition, bad JSON configuration files will lead to unexpected behavior. You've been warned!

Ce plug-in est en phase de développement initial, et n'a été que partiellement testé, avec seulement certains types de dispositifs Domoticz. De plus, un fichier de configuration JSON incorrect va provoquer des effets inattendus, voire rigolos. Vous avez été prévenus !

## Prerequisites / Prérequis

- Domoticz 2020.0 or higher (but lower version could also work)
- Make sure that your Domoticz supports Python plug-ins (https://www.domoticz.com/wiki/Using_Python_plugins)

- Domoticz 2022.0 ou supérieurs (les versions précédentes peuvent aussi fonctionner)
- Vérifiez que votre version de Domoticz supporte les plug-ins Python (https://www.domoticz.com/wiki/Using_Python_plugins)

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

## plug-in update / Mise à jour du plug-in

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

## Configuration

plug-in uses an external JSON configuration file to map MQTT topics to Domoticz devices. Here's an example of syntax:

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
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    },
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0;0;0"},
        "mapping": {"item": "temperature;humidity;~0"}
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

When empty or `~*`, `mapping` -> `item` indicates that payload is not in a JSON format. Extracted value is content of payload. Default value is set in `default` and mapping values in `values`. Here, when payload is `close`, device is set to `1`.

In short, when receiving topic `volvo/xx-999-xx/binary_sensor/any_window_open/state` with value `close`, a switch device `(244/73/11)` is set to off, else on.

When `default` is not specified, the extracted value will be directly loaded in associated device.

`Car windows` représente le nom du dispositif Domoticz à créer. `type`, `subtype` et `switchtype` contiennent les types/subtypes/switchtypes du dispositif à créer. La liste des valeurs supportées est disponible à (https://www.domoticz.com/wiki/Developing_a_Python_plugin#Available_Device_Types).

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

Here, `options` contains the options used to create the device. Obviously, I don't find a full list, I put a partial one at end of this document. 

Dans cet exemple, `options` contient les options utilisées pour créer le dispositif. Je n'ai malheureusement pas trouvé de liste complète, j'ai mis une ébauche à la fin de ce document.

```ts
    "Beed room temperature": {
        "topic": "beedRoom",
        "type": "80", "subtype": "5", "switchtype": "0",
        "mapping": {"item": "temperature", "multiplier": 0.1, "digits": 1}
    }
```

This time, payload is in JSON format (`item` is not empty). This mean that the value will be extracted from `temperature` payload item, at the root level. `ENERGY/Power` in later example means that value will be extracted in `Power` item of `Energy` root item.

`multiplier` is optional, and gives the factor to apply to numeric value (here `0.1`, equivalent to divided by 10).
'digits' is also optional, and gives the number of decimal digits to round value to.

Cette fois, le contenu est au format JSON (`item` n'est pas vide). La valeur extraite sera prise dans l'item `temperature` du contenu, au niveau supérieur. `ENERGY/Power` dans l'exemple suivant indique que la valeur sera extraite de l'item `Power` de l'item `Energy`.

`multiplier` est optionnel et indique le facteur à appliquer à la valeur numérique (ici `0.1`, équivalent à diviser par 10).
'digits' est également optionnel et indique le nombre de décimales à utiliser pour arrondir la valeur.

```ts
    "Kitchen temperature": {"topic": "zigbee2mqtt/Kitchen",
        "type": "82", "subtype": "5", "switchtype": "0",
        "initial": {"svalue": "0.0;0;0"},
        "mapping": {"item": "temperature;humidity;~0"}
    }
```

To specify multiple values, separate them with a `;`, like in `temperature;humidity`. Device value will be set with the concatenation of the two items.

Note that you also can specify constants in the list, prefixing them with `~`. For example `total;~0;~0;~0;power;~0` to generate a kWh counter sValue.

Should you want to change only part of sValue, you may use `~` alone to keep current value. For example, `value;~` will insert content of value item and keep second part of sValue.

To set initial sValue or nValue, you can use "initial": {"nvalue": 123} or "initial": {"svalue": "abc"} or both.

Pour indiquer des valeurs multiples, séparez-les par des `;`, comme dans `temperature;humidity`. La valeur chargée sera la concaténation des deux items.

Noter que vous pouvez aussi insérer des constantes, en les préfixant par `~`. Par exemple `total;~0;~0;~0;power;~0` pour spécifier le contenu de type sValue d'un compteur en KWh.

Si vous voulez ne changer qu'une partie de la variable sValue d'un dispositif, vous pouvez utiliser `~` seul pour conserver une partie existante. Par exemple, `value;~` va insérer le contenu de l'item value et conserver la seconde partie de sValue.

Pour définir une valeur initiale pour nvalue ou svalue sur un dispositif, vous pouvez utiliser "initial": {"nvalue": 123} ou "initial": {"svalue": "abc"} ou les deux.

You may need to create multiple devices from the same topic. In this case, use optional `key` item to specify a "virtual" key. This key can be anything, as long as it is unique and different from topics. For example:

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
will map properly a json payload as / va décoder proprement un message json comme `{"input1":{"value":false},"input2":{"value":false}}`

In certain cases, payload contains lists (represented by `[]` delimiters). In this case, you have to specify either list index to use (starting with 1) or `*` in order to analyze all list items.

Dans certains cas, la charge contient une liste (représentée par les délimiteurs `[]`). Dans ce cas, vous devez spécifier soit l'index de la liste à utiliser (démarrant à 1), soit `*`pour analyser l'ensemble des éléments de la liste.

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

`topic` contains the topic to send the value to (defaults to primary topic if not specified). Set it to empty to ignore SET requests without error message.
`payload` contains the payload to send (defaults to `#`). The `#` character will be replaced by translated value (`Forced` in this example if Domoticz devices holds 20 in its level).

`topic` contient le topic vers lequel la valeur sera envoyée (par défaut, on utilisera celui du dispositif). Mettez le vide pour ignorer les demandes de modification sans afficher d'erreur. 

`payload` contient la valeur à envoyer (par défaut `#`). Le caractère `#` sera remplacé par la valeur associée (Dans cet exemple, `Forced` si le dispositif Domoticz contient un niveau 20).

It's also possible to execute a bash command through `command` tag. In this case, unless you explicitely specify `topic`, no MQTT set will be send. Value to set will replace the `#`in command.

Il est également possible d'exécuter une commande bash avec le tag `command`. Dans ce cas, il n'y aura pas de set MQTT, sauf si vous specifiez explicitement le tag `topic`. Les `#` présents dans la commande seront remplacés par la valeur à affecter.

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

Note that bash command will be executed with a default folder equal to Domoticz root folder. Add `plugin/MqttMapper/` in command if you wish to execute commands into MqttMQpper context. You may also specify a full path like `/home/user/...`.

Noter que la commande bash sera executée par défaut dans le répertoire de Domoticz. Ajoutez `plugin/MqttMapper/`  dans la commande si vous souhaitez l'exécuter dans le contexte de MqttMapper. Vous pouvez aussi spcifier un chemin complet comme `/home/user/...`.

If value to set is a float, lot of digits will be given to the command. A way to round it is to use `bc` command (`sudo apt install bc` if not already installed). Here's an example (replace `1` in `scale=1\ by number of digits you want so see after decimal point):

Si la valeur à définir est un nombre flottant, de nombreuses décimales seront passées à la commande. Une façon de l'arrondir est d'utiliser la commande `bc` (à installer par `sudo apt install bc` si elle n'existe pas). Voici un exemple (remplacer `1` dans  `scale=1\ par le nombre de décimales souhaitées) :

```ts
#!/bin/bash
value=$(echo "scale=1; $1 / 1" | bc)
echo "Received $value"
```

You may also use "'digit': n" in set command parameters to round value:

Vous pouvez aussi utiliser "'digit': n" dans les parramtres de la commande set pour arrondir la valeur:

```ts
        "set": {"topic": "topic/xxx", "payload": {"value":"#"}, "digits": 2}
```

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

## JSON files check/Vérification des fichiers JSON

You may run checkJsonFiles.py to scan JSON file for important errors. It'll scan all JSON files in the current folder and display errors. Fix them until no errors are found.

Vous pouvez vérifier les erreurs les plus flagrantes des fichiers JSON avec le script checkJsonFiles.py. Il va scanner l'ensemble des .JSON présents dans le répertoire courant et afficher les erreurs. Corrigez jusqu'à ce qu'aucune erreur ne soit affichée.

## Debug tool/Outil de déverminage

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

Pour aider au déverminage des problèmes de MQTTMapper ou des fichiers de configuration, un script nommé dumpMqttMapperValues.py est disponible dans le répertoire du plugin. Il va chercher les fichiers de configuration dans le répertoire courant, afficher leur contenu, les données de l'API ddomoticz et de la base de données, ainsi que les topics MQTT associés sur l'écran. Il détecte aussi les noms de dispositifs dupliqués, qui apportent des effets de bord aussi amusants qu'inattendus ;-)

Copiez/collez (ou redirigez) les messages pour me les envoyer.

Les options suivantes sont disponibles :
    [--input=<Fichier(s) a analyser>]: fichier(s) en entrée (peut être répété, par défaut on utilise *.json.parameters). Peut être utilisé lorsque plusieurs instances du plugin sont lancées depuis le même répertoire.
    [--wait=<minutes>]: attend les changements des topics pendant <minutes>. Peut être utilisé pour les topics qui n'ont pas l'indicateur "retain", pour attendre un changement suffisament longtemps.
    [--url=<URL de Domoticz>]: utiliser cette URL Domoticz au lieu du défaut http://127.0.0.1:8080/. Vous pouvez spécifier si besoin username:password. Noubliez pas http:// ou https://.
    [--checkend]: vérifie les dispositfs partageant la même fin de nom. En plus des dispositifs possédant le même nom, cette option permet de détecter les mêmes terminaisons.
    [--keep]: conserve la copie de la base et la réponse de l'API
    [--debug]: affiche les messages de déverminage
    [--help]: affiche ce message d'aide (en version anglaise)

Pour afficher l'ensemble des données, 2 extensions Python peuvent être installées sur la machine (le script peut fonctionner sans elles, mais seules des informations partielles seront affichées). Si elles ne sont pas installées, vous aurez un message. Vous pouvez les nstaller en utilisant les commandes "pip3 install paho-mqtt" et "pip3 install sqlite3". Si vous avez un environnement managé, remplacez ces commandes par "sudo apt install python3-paho-mqtt" et "sudo apt install python3-sqlite3".

### findDomoticzTypes

This tool allow to find information about types, subtypes and switch type, giving integer value (in decimal or hexa-decimal), or string (using a regular expression). It's even possible to get full list of supported combinations. It will display values, names, nValue and sValue(s) for each supported configuration.

Cet outil permet de trouver des informations sur les types, subtypes et switchtypes, à partir d'une valeur décimale, hexa-décimale ou chaîne de caractères (en utilisation une expression régulière) Il est même possible d'obtenir la liste des combinaisons supportées. Les valeurs, noms, nValue et sValue(s) pour chaque configuration supportées.

# Examples / Exemples
Here are some examples that may be useful. Each examples show (part of) setup file, content of topic used, Domoticz device value, and result description / Vous trouverez ci-dessous des exemples utiles. Chaque exemple montre (une partie de) la configuration, le contenu du topic utilisé, la valeur du dispositif Domoticz et la description du résultat

## Full topic content / Totalité du contenu du topic
```
Setup / Configuration:
{"device": {"topic": "sensor/state",  "mapping": {"item": ""}}}

Topic content / Contenu du topic:
active since 1 hour

Domoticz device value / Valeur du dispositif Domoticz:
[device] -> active since 1 hour
```

## One JSON item / Un item du message JSON
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature"}}}

Topic content / Contenu du topic:
{"temperature": 19, "humidity":70}

Domoticz device value / Valeur du dispositif Domoticz:
 19 
```

## With multiplier / Avec Multiplicateur
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature",  "multiplier": 0.1}}}

Topic content / Contenu du topic:
{"temperature": 195, "humidity":700}

Domoticz device value / Valeur du dispositif Domoticz:
19.5
```

## With mapping / Avec association
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"}}}}

Topic content / Contenu du topic:
{"mode": "Auto"}

Domoticz device value / Valeur du dispositif Domoticz:
 10 
```

## With default value / Avec valeur par défaut
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "mode",  "values": {"Off": "0",  "Auto": "10",  "Forced": "20"},  "default": "0"}}}

Topic content / Contenu du topic:
{"mode": "Unknown"}

Domoticz device value / Valeur du dispositif Domoticz:
 0 
```

## With multiple items / Avec plusieurs items
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity"}}}

Topic content / Contenu du topic:
{"temperature": 19, "humidity":70}

Domoticz device value / Valeur du dispositif Domoticz:
19;70
```

## With multiple items and constant / Avec plusieurs items et constante
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "temperature;humidity;~3"}}}

Topic content / Contenu du topic:
{"temperature": 19, "humidity":70}

Domoticz device value / Valeur du dispositif Domoticz:
19;70;3
```

## One topic/Multiple devices / Un topic/Plusieurs dispositifs
```
Setup / Configuration:
{"device1":{"topic": "sensor/state", "key":"sensor/state-1", "mapping": {"item": "temperature"}},
"device2":{"topic": "sensor/state", "key":"sensor/state-2",  "mapping": {"item": "humitidy"}}}

Topic content / Contenu du topic:
{"temperature": 19, "humidity":70}

Domoticz device value / Valeur du dispositif Domoticz:
[device1] ->  19
[device2] ->  70
```

## Item deeper in JSON message / L'item est enfoui dans le message JSON
```
Setup / Configuration:
{"device":{"topic": "sensor/state",  "mapping": {"item": "sensor1/lastRead/temperature"}}}

Topic content / Contenu du topic:
{"sensor1": {"counter" : 123456, "lastRead" : {"temperature": 19, "humidity":70}}}

Domoticz device value / Valeur du dispositif Domoticz:
 19 
```

## Item with list in JSON message / L'item est dans une liste du message JSON
```
Setup / Configuration:
{"device":{"topic": "gateway/12345/event/up", "mapping": {"item": "rxInfo/*/rssi"}}}

Topic content / Contenu du topic:
{"rxInfo": [{"rssi": -69, "snr": 11.2, "channel": 2}]}

Domoticz device value / Valeur du dispositif Domoticz:
 -69 
```
