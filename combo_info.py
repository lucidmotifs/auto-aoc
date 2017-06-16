# gneral utltily
import logging

# keyboard hooks
import keyboard
import pyautogui

# timing module
from timeit import default_timer as timer

# from this application
from rotation import Rotation
from ability import Ability
from ability import COOLDOWN_ACTIONS
from combo import Combo

# classes and combos
from conqueror.combos import *
from conqueror.abilities import *


## Conqueror DPS Rotation
conq_dps = Rotation()

# Combos
conq_dps.use( Breech(4) ).at( 1 )
conq_dps.use( Whirlwind() ).at( 2, 6 )
conq_dps.use( BloodyHack(5) ).at( 3, 5, 7 )
conq_dps.use( Bloodbath(6) ).at( 4 )

# Abilities
conq_dps.use( )
