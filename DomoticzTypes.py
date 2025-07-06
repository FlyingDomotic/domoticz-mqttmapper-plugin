class DomoticzTypes:
    version = "25.6.24-1"

    switchTypeList = [
        16,                                                         # Lighting1
        17,                                                         # Lighting2
        18,                                                         # Lighting3
        19,                                                         # Lighting4
        20,                                                         # Lighting5
        21,                                                         # Lighting6
        23,                                                         # Fan
        24,                                                         # Curtain
        25,                                                         # Blinds
        26,                                                         # RFY
        27,                                                         # HomeConfort
        31,                                                         # Hunter
        32,                                                         # Security1
        33,                                                         # Security2
        48,                                                         # Remote
        65,                                                         # Thermostat2
        66,                                                         # Thermostat3
        114,                                                        # FS20
        241,                                                        # ColorSwitch
        244                                                         # GeneralSwitch
    ]

    hasNvalueList = [
        [16, -1, -1],                                               # Lighting1
        [17, 62, -1],                                               # Lighting2/TypeSelector
        [17, 73, 0],                                                # Lighting2/GeneralSwitch/OnOff
        [17, 73, 1],                                                # Lighting2/GeneralSwitch/Doorbell
        [17, 73, 2],                                                # Lighting2/GeneralSwitch/Contact
        [17, 73, 3],                                                # Lighting2/GeneralSwitch/Blinds
        [17, 73, 4],                                                # Lighting2/GeneralSwitch/X10Siren
        [17, 73, 5],                                                # Lighting2/GeneralSwitch/SMOKEDETECTOR
        [17, 73, 7],                                                # Lighting2/GeneralSwitch/Dimmer
        [17, 73, 8],                                                # Lighting2/GeneralSwitch/Motion
        [17, 73, 9],                                                # Lighting2/GeneralSwitch/PushOn
        [17, 73, 10],                                               # Lighting2/GeneralSwitch/PushOff
        [17, 73, 11],                                               # Lighting2/GeneralSwitch/DoorContact
        [17, 73, 12],                                               # Lighting2/GeneralSwitch/Dusk
        [17, 73, 13],                                               # Lighting2/GeneralSwitch/BlindsPercentage
        [17, 73, 14],                                               # Lighting2/GeneralSwitch/VenetianBlindsUS
        [17, 73, 15],                                               # Lighting2/GeneralSwitch/VenetianBlindsEU
        [17, 73, 17],                                               # Lighting2/GeneralSwitch/Media
        [17, 73, 18],                                               # Lighting2/GeneralSwitch/Selector
        [17, 73, 19],                                               # Lighting2/GeneralSwitch/DoorLock
        [17, 73, 20],                                               # Lighting2/GeneralSwitch/DoorLockInverted
        [17, 73, 21],                                               # Lighting2/GeneralSwitch/BlindsPercentageWithStop
        [18, -1, -1],                                               # Lighting3
        [19, -1, -1],                                               # Lighting4
        [20, -1, -1],                                               # Lighting5
        [21, -1, -1],                                               # Lighting6
        [22, -1, -1],                                               # Chime
        [23, -1, -1],                                               # Fan
        [24, -1, -1],                                               # Curtain
        [25, -1, -1],                                               # Blinds
        [26, -1, -1],                                               # RFY
        [27, -1, -1],                                               # HomeConfort
        [31, -1, -1],                                               # Hunter
        [32, -1, -1],                                               # Security1
        [33, -1, -1],                                               # Security2
        [48, -1, -1],                                               # Remote
        [65, -1, -1],                                               # Thermostat2
        [66, -1, -1],                                               # Thermostat3
        [69, -1, -1],                                               # Evohome
        [72, -1, -1],                                               # Radiator1
        [81, -1, -1],                                               # HUM
        [114, -1, -1],                                              # FS20
        [241, -1, -1],                                              # ColorSwitch
        [243, 3, -1],                                               # General/SoilMoisture
        [243, 4, -1],                                               # General/LeafWetness
        [243, 20, -1],                                              # General/ZWaveThermostatMode
        [243, 21, -1],                                              # General/ZWaveThermostatFanMode
        [243, 22, -1],                                              # General/Alert
        [243, 32, -1],                                              # General/ZWaveAlarm
        [243, 35, -1],                                              # General/ZWaveThermostatOperatingState
        [244, 62, -1],                                              # GeneralSwitch/TypeSelector
        [244, 73, 0],                                               # GeneralSwitch/GeneralSwitch/OnOff
        [244, 73, 1],                                               # GeneralSwitch/GeneralSwitch/Doorbell
        [244, 73, 2],                                               # GeneralSwitch/GeneralSwitch/Contact
        [244, 73, 3],                                               # GeneralSwitch/GeneralSwitch/Blinds
        [244, 73, 4],                                               # GeneralSwitch/GeneralSwitch/X10Siren
        [244, 73, 5],                                               # GeneralSwitch/GeneralSwitch/SMOKEDETECTOR
        [244, 73, 7],                                               # GeneralSwitch/GeneralSwitch/Dimmer
        [244, 73, 8],                                               # GeneralSwitch/GeneralSwitch/Motion
        [244, 73, 9],                                               # GeneralSwitch/GeneralSwitch/PushOn
        [244, 73, 10],                                              # GeneralSwitch/GeneralSwitch/PushOff
        [244, 73, 11],                                              # GeneralSwitch/GeneralSwitch/DoorContact
        [244, 73, 12],                                              # GeneralSwitch/GeneralSwitch/Dusk
        [244, 73, 13],                                              # GeneralSwitch/GeneralSwitch/BlindsPercentage
        [244, 73, 14],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsUS
        [244, 73, 15],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsEU
        [244, 73, 17],                                              # GeneralSwitch/GeneralSwitch/Media
        [244, 73, 18],                                              # GeneralSwitch/GeneralSwitch/Selector
        [244, 73, 19],                                              # GeneralSwitch/GeneralSwitch/DoorLock
        [244, 73, 20],                                              # GeneralSwitch/GeneralSwitch/DoorLockInverted
        [244, 73, 21],                                              # GeneralSwitch/GeneralSwitch/BlindsPercentageWithStop
        [249, -1, -1]                                               # AirQuality
    ]

    hasSvalueList = [
        [17, 62, -1],                                               # Lighting2/TypeSelector
        [17, 73, 7],                                                # Lighting2/GeneralSwitch/Dimmer
        [17, 73, 13],                                               # Lighting2/GeneralSwitch/BlindsPercentage
        [17, 73, 14],                                               # Lighting2/GeneralSwitch/VenetianBlindsUS
        [17, 73, 15],                                               # Lighting2/GeneralSwitch/VenetianBlindsEU
        [17, 73, 18],                                               # Lighting2/GeneralSwitch/Selector
        [17, 73, 21],                                               # Lighting2/GeneralSwitch/BlindsPercentageWithStop
        [19, -1, -1],                                               # Lighting4
        [20, -1, -1],                                               # Lighting5
        [21, -1, -1],                                               # Lighting6
        [64, -1, -1],                                               # Thermostat1
        [67, -1, -1],                                               # Thermostat4
        [68, -1, -1],                                               # EvohomeRelay
        [69, -1, -1],                                               # Evohome
        [70, -1, -1],                                               # EvohomeZone
        [71, -1, -1],                                               # EvohomeWater
        [72, -1, -1],                                               # Radiator1
        [78, -1, -1],                                               # BBQ
        [79, -1, -1],                                               # TEMP_RAIN
        [80, -1, -1],                                               # TEMP
        [81, -1, -1],                                               # HUM
        [82, -1, -1],                                               # TEMP_HUM
        [84, -1, -1],                                               # TEMP_HUM_BARO
        [85, -1, -1],                                               # RAIN
        [86, -1, -1],                                               # WIND
        [87, -1, -1],                                               # UV
        [89, -1, -1],                                               # CURRENT
        [90, -1, -1],                                               # ENERGY
        [91, -1, -1],                                               # CURRENTENERGY
        [92, -1, -1],                                               # POWER
        [93, -1, -1],                                               # WEIGHT
        [112, -1, -1],                                              # RFXSensor
        [113, -1, -1],                                              # RFXMeter
        [241, -1, -1],                                              # ColorSwitch
        [242, -1, -1],                                              # Setpoint
        [243, 1, -1],                                               # General/Visibility
        [243, 2, -1],                                               # General/SolarRadiation
        [243, 6, -1],                                               # General/Percentage
        [243, 7, -1],                                               # General/Fan
        [243, 8, -1],                                               # General/Voltage
        [243, 9, -1],                                               # General/Pressure
        [243, 19, -1],                                              # General/TextStatus
        [243, 22, -1],                                              # General/Alert
        [243, 23, -1],                                              # General/Current
        [243, 24, -1],                                              # General/SoundLevel
        [243, 26, -1],                                              # General/Baro
        [243, 27, -1],                                              # General/Distance
        [243, 28, -1],                                              # General/CounterIncremental
        [243, 29, -1],                                              # General/Kwh
        [243, 30, -1],                                              # General/Waterflow
        [243, 31, -1],                                              # General/Custom
        [243, 32, -1],                                              # General/ZWaveAlarm
        [243, 33, -1],                                              # General/ManagedCounter
        [244, 62, -1],                                              # GeneralSwitch/TypeSelector
        [244, 73, 7],                                               # GeneralSwitch/GeneralSwitch/Dimmer
        [244, 73, 13],                                              # GeneralSwitch/GeneralSwitch/BlindsPercentage
        [244, 73, 14],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsUS
        [244, 73, 15],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsEU
        [244, 73, 18],                                              # GeneralSwitch/GeneralSwitch/Selector
        [244, 73, 21],                                              # GeneralSwitch/GeneralSwitch/BlindsPercentageWithStop
        [246, -1, -1],                                              # Lux
        [247, -1, -1],                                              # TEMP_BARO
        [248, -1, -1],                                              # Usage
        [250, -1, -1],                                              # P1Power
        [251, -1, -1],                                              # P1Gas
        [252, -1, -1],                                              # YouLess
        [253, -1, -1],                                              # Rego6XXTemp
        [254, -1, -1]                                               # Rego6XXValue
    ]

    canBeSetList = [
        [16, -1, -1],                                               # Lighting1
        [17, 62, -1],                                               # Lighting2/TypeSelector
        [17, 73, 0],                                                # Lighting2/GeneralSwitch/OnOff
        [17, 73, 1],                                                # Lighting2/GeneralSwitch/Doorbell
        [17, 73, 2],                                                # Lighting2/GeneralSwitch/Contact
        [17, 73, 3],                                                # Lighting2/GeneralSwitch/Blinds
        [17, 73, 4],                                                # Lighting2/GeneralSwitch/X10Siren
        [17, 73, 5],                                                # Lighting2/GeneralSwitch/SMOKEDETECTOR
        [17, 73, 7],                                                # Lighting2/GeneralSwitch/Dimmer
        [17, 73, 8],                                                # Lighting2/GeneralSwitch/Motion
        [17, 73, 9],                                                # Lighting2/GeneralSwitch/PushOn
        [17, 73, 10],                                               # Lighting2/GeneralSwitch/PushOff
        [17, 73, 11],                                               # Lighting2/GeneralSwitch/DoorContact
        [17, 73, 12],                                               # Lighting2/GeneralSwitch/Dusk
        [17, 73, 13],                                               # Lighting2/GeneralSwitch/BlindsPercentage
        [17, 73, 14],                                               # Lighting2/GeneralSwitch/VenetianBlindsUS
        [17, 73, 15],                                               # Lighting2/GeneralSwitch/VenetianBlindsEU
        [17, 73, 17],                                               # Lighting2/GeneralSwitch/Media
        [17, 73, 18],                                               # Lighting2/GeneralSwitch/Selector
        [17, 73, 19],                                               # Lighting2/GeneralSwitch/DoorLock
        [17, 73, 20],                                               # Lighting2/GeneralSwitch/DoorLockInverted
        [17, 73, 21],                                               # Lighting2/GeneralSwitch/BlindsPercentageWithStop
        [18, -1, -1],                                               # Lighting3
        [19, -1, -1],                                               # Lighting4
        [20, -1, -1],                                               # Lighting5
        [21, -1, -1],                                               # Lighting6
        [242, -1, -1],                                              # Setpoint
        [243, 19, -1],                                              # General/TextStatus
        [244, 62, -1],                                              # GeneralSwitch/TypeSelector
        [244, 73, 0],                                               # GeneralSwitch/GeneralSwitch/OnOff
        [244, 73, 1],                                               # GeneralSwitch/GeneralSwitch/Doorbell
        [244, 73, 2],                                               # GeneralSwitch/GeneralSwitch/Contact
        [244, 73, 3],                                               # GeneralSwitch/GeneralSwitch/Blinds
        [244, 73, 4],                                               # GeneralSwitch/GeneralSwitch/X10Siren
        [244, 73, 5],                                               # GeneralSwitch/GeneralSwitch/SMOKEDETECTOR
        [244, 73, 7],                                               # GeneralSwitch/GeneralSwitch/Dimmer
        [244, 73, 8],                                               # GeneralSwitch/GeneralSwitch/Motion
        [244, 73, 9],                                               # GeneralSwitch/GeneralSwitch/PushOn
        [244, 73, 10],                                              # GeneralSwitch/GeneralSwitch/PushOff
        [244, 73, 11],                                              # GeneralSwitch/GeneralSwitch/DoorContact
        [244, 73, 12],                                              # GeneralSwitch/GeneralSwitch/Dusk
        [244, 73, 13],                                              # GeneralSwitch/GeneralSwitch/BlindsPercentage
        [244, 73, 14],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsUS
        [244, 73, 15],                                              # GeneralSwitch/GeneralSwitch/VenetianBlindsEU
        [244, 73, 17],                                              # GeneralSwitch/GeneralSwitch/Media
        [244, 73, 18],                                              # GeneralSwitch/GeneralSwitch/Selector
        [244, 73, 19],                                              # GeneralSwitch/GeneralSwitch/DoorLock
        [244, 73, 20],                                              # GeneralSwitch/GeneralSwitch/DoorLockInverted
        [244, 73, 21]                                               # GeneralSwitch/GeneralSwitch/BlindsPercentageWithStop
    ]

    # Init class
    def __init__(self):
        pass

    # Returns True if deviceType is a switch
    def isSwitch(self, deviceType):
        return int(deviceType) in self.switchTypeList

    # Return True if device Type/subType/switchType is in a given list
    def isInList(self, deviceType, deviceSubType, deviceSwitchType, listToUse):
        for deviceChar in listToUse:
            if int(deviceType) == deviceChar[0]:                    # Device type is found
                if deviceChar[1] == -1:                             # Any subType, return True
                    return True
                if int(deviceSubType) == deviceChar[1]:             # Device subType is found
                    if deviceChar[2] == -1:                         # Device switchType is found
                        return True
                    if int(deviceSwitchType) == deviceChar[2]:      # Device switchType is found
                        return True
        return False

    # Returns True if device Type/subType/switchType correspond to a device having nValue
    def hasNvalueData(self, deviceType, deviceSubType, deviceSwitchType):
        return self.isInList(deviceType, deviceSubType, deviceSwitchType, self.hasNvalueList)

    # Returns True if device Type/subType/switchType correspond to a device having sValue
    def hasSvalueData(self, deviceType, deviceSubType, deviceSwitchType):
        return self.isInList(deviceType, deviceSubType, deviceSwitchType, self.hasSvalueList)

    # Returns True if device Type/subType/switchType correspond to a device we can set
    def canBeSet(self, deviceType, deviceSubType, deviceSwitchType):
        return self.isInList(deviceType, deviceSubType, deviceSwitchType, self.canBeSetList)

    # Returns True if device Type/subType/switchType correspond to a switch with sValue as level
    def isLevelSwitch(self, deviceType, deviceSubType, deviceSwitchType):
        return self.isSwitch(deviceType) and self.hasSvalueData(deviceType, deviceSubType, deviceSwitchType)