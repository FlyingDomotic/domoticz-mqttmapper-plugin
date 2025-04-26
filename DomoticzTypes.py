class DomoticzTypes:
    version = "25.4.26-1"

    switchTypeList = [ # List of types being switches
        16, # Lighting1
        17, # Lighting2
        19, # Lighting4
        20, # Lighting5
        21, # Lighting6
        244 # GeneralSwitch
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
        return int(deviceType) in self.switchTypeList

    # Returns True if device Type/subType/switchType correspond to a device having sValue as level
    def isLevelSwitch(self, deviceType, deviceSubType, deviceSwitchType):
        for deviceChar in self.switchLevelList:
            if int(deviceType) == deviceChar[0]: # Device type is found
                if deviceChar[1] == -1: # Any subType, return True
                    return True
                if int(deviceSubType) == deviceChar[1]: # Device subType is found
                    if deviceChar[2] == -1: # Device switchType is found
                        return True
                    if int(deviceSwitchType) == deviceChar[2]: # Device switchType is found
                        return True
        return False
