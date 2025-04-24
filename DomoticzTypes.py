class DomoticzTypes:
    version = "25.4.24-1"

    switchTypeList = [ # List of types being switches
        16, # Lighting1
        17, # Lighting2
        19, # Lighting4
        20, # Lighting5
        21, # Lighting6
        244 # GeneralSwitch
    ]

    switchStateList = [ # List of type/subTypes/switchTypes of switches using nValue to store state (-1 meaning don't care)
        [16, -1, -1], # Lighting1
        [17, 73, 0], # Lighting2/GeneralSwitch/OnOff
        [17, 73, 1], # Lighting2/GeneralSwitch/Doorbell
        [17, 73, 2], # Lighting2/GeneralSwitch/Contact
        [17, 73, 3], # Lighting2/GeneralSwitch/Blinds
        [17, 73, 4], # Lighting2/GeneralSwitch/X10Siren
        [17, 73, 5], # Lighting2/GeneralSwitch/SMOKEDETECTOR
        [17, 73, 7], # Lighting2/GeneralSwitch/Dimmer
        [17, 73, 8], # Lighting2/GeneralSwitch/Motion
        [17, 73, 9], # Lighting2/GeneralSwitch/PushOn
        [17, 73, 10], # Lighting2/GeneralSwitch/PushOff
        [17, 73, 11], # Lighting2/GeneralSwitch/DoorContact
        [17, 73, 12], # Lighting2/GeneralSwitch/Dusk
        [17, 73, 13], # Lighting2/GeneralSwitch/BlindsPercentage
        [17, 73, 14], # Lighting2/GeneralSwitch/VenetianBlindsUS
        [17, 73, 15], # Lighting2/GeneralSwitch/VenetianBlindsEU
        [17, 73, 17], # Lighting2/GeneralSwitch/Media
        [17, 73, 18], # Lighting2/GeneralSwitch/Selector
        [17, 73, 19], # Lighting2/GeneralSwitch/DoorLock
        [17, 73, 20], # Lighting2/GeneralSwitch/DoorLockInverted
        [17, 73, 21], # Lighting2/GeneralSwitch/BlindsPercentageWithStop
        [19, -1, -1], # Lighting4
        [20, -1, -1], # Lighting5
        [21, -1, -1], # Lighting6
        [244, 73, 0], # GeneralSwitch/GeneralSwitch/OnOff
        [244, 73, 1], # GeneralSwitch/GeneralSwitch/Doorbell
        [244, 73, 2], # GeneralSwitch/GeneralSwitch/Contact
        [244, 73, 3], # GeneralSwitch/GeneralSwitch/Blinds
        [244, 73, 4], # GeneralSwitch/GeneralSwitch/X10Siren
        [244, 73, 5], # GeneralSwitch/GeneralSwitch/SMOKEDETECTOR
        [244, 73, 7], # GeneralSwitch/GeneralSwitch/Dimmer
        [244, 73, 8], # GeneralSwitch/GeneralSwitch/Motion
        [244, 73, 9], # GeneralSwitch/GeneralSwitch/PushOn
        [244, 73, 10], # GeneralSwitch/GeneralSwitch/PushOff
        [244, 73, 11], # GeneralSwitch/GeneralSwitch/DoorContact
        [244, 73, 12], # GeneralSwitch/GeneralSwitch/Dusk
        [244, 73, 13], # GeneralSwitch/GeneralSwitch/BlindsPercentage
        [244, 73, 14], # GeneralSwitch/GeneralSwitch/VenetianBlindsUS
        [244, 73, 15], # GeneralSwitch/GeneralSwitch/VenetianBlindsEU
        [244, 73, 17], # GeneralSwitch/GeneralSwitch/Media
        [244, 73, 18], # GeneralSwitch/GeneralSwitch/Selector
        [244, 73, 19], # GeneralSwitch/GeneralSwitch/DoorLock
        [244, 73, 20], # GeneralSwitch/GeneralSwitch/DoorLockInverted
        [244, 73, 21] # GeneralSwitch/GeneralSwitch/BlindsPercentageWithStop
    ]

    switchLevelList = [ # List of type/subTypes/switchTypes of switches using nValue to store state (-1 meaning don't care)
        [17, 62, -1], # Lighting2/TypeSelector
        [17, 73, 7], # Lighting2/GeneralSwitch/Dimmer
        [17, 73, 13], # Lighting2/GeneralSwitch/BlindsPercentage
        [17, 73, 14], # Lighting2/GeneralSwitch/VenetianBlindsUS
        [17, 73, 15], # Lighting2/GeneralSwitch/VenetianBlindsEU
        [17, 73, 18], # Lighting2/GeneralSwitch/Selector
        [17, 73, 21], # Lighting2/GeneralSwitch/BlindsPercentageWithStop
        [19, -1, -1], # Lighting4
        [20, -1, -1], # Lighting5
        [21, -1, -1], # Lighting6
        [244, 62, -1], # GeneralSwitch/TypeSelector
        [244, 73, 7], # GeneralSwitch/GeneralSwitch/Dimmer
        [244, 73, 13], # GeneralSwitch/GeneralSwitch/BlindsPercentage
        [244, 73, 14], # GeneralSwitch/GeneralSwitch/VenetianBlindsUS
        [244, 73, 15], # GeneralSwitch/GeneralSwitch/VenetianBlindsEU
        [244, 73, 18], # GeneralSwitch/GeneralSwitch/Selector
        [244, 73, 21] # GeneralSwitch/GeneralSwitch/BlindsPercentageWithStop
    ]

    # Init class
    def __init__(self):
        pass

    # Returns True if deviceType is a switch
    def isSwitch(self, deviceType):
        return deviceType in self.switchTypeList

    # Returns True if device Type/subType/switchType correspond to a device having nValue as switch state
    def isStateSwitch(self, deviceType, deviceSubType, deviceSwitchType):
        for deviceChar in self.switchStateList:
            if deviceType == deviceChar[0]: # Device type is found
                if deviceChar[1] == -1: # Any subType, return True
                    return True
                if deviceChar[1] == deviceSubType: # Device subType is found
                    if deviceChar[2] == -1: # Device switchType is found
                        return True
                    if deviceChar[2] == deviceSwitchType: # Device switchType is found
                        return True
        return False

    # Returns True if device Type/subType/switchType correspond to a device having sValue as level
    def isLevelSwitch(self, deviceType, deviceSubType, deviceSwitchType):
        for deviceChar in self.switchLevelList:
            if deviceType == deviceChar[0]: # Device type is found
                if deviceChar[1] == -1: # Any subType, return True
                    return True
                if deviceChar[1] == deviceSubType: # Device subType is found
                    if deviceChar[2] == -1: # Device switchType is found
                        return True
                    if deviceChar[2] == deviceSwitchType: # Device switchType is found
                        return True
        return False
