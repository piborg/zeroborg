# Button map for IR remote using ZeroBorg
# You can generate a new version of this script using zbSaveIr.py

# Helper function for pulling in other maps to this one
import sys
def MakeLocalMap(otherMap, prefix):
    thismodule = sys.modules[__name__]
    for buttonName in otherMap.__dict__.keys():
        if buttonName.startswith('IR_'):
            code = otherMap.__dict__[buttonName]
            name = 'IR_' + prefix + '_' + buttonName[3:]
            setattr(thismodule, name, code)

# Pull in the standard examples with custom names
import zbIrMapRMT_VB100L as SONY_NETFLIX
import zbIrMapRM_ED009 as SONY_TV
import zbIrMapBN59_01015A as SAMSUNG_TV
MakeLocalMap(SONY_NETFLIX, 'SONY_NETFLIX')
MakeLocalMap(SONY_TV, 'SONY_TV')
MakeLocalMap(SAMSUNG_TV, 'SAMSUNG_TV')
