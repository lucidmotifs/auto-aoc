# gneral utltily
import logging
import random
import generic
import time
import threading

# keyboard hooks
import keyboard
import pyautogui
import pywinauto

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


logging.basicConfig(
    format='%(message)s',
    filename='output.txt',
    filemode='w',
    level=logging.DEBUG)


## Conqueror DPS Rotation
conq_dps = Rotation()
conq_dps.repeat = True
conq_dps.repeat_count = 2

# Combos
conq_dps.use( Breech(4) ).at( 1 )
conq_dps.use( Whirlwind() ).at( 2, 6 )
conq_dps.use( BloodyHack(6) ).at( 3 )
conq_dps.use( BloodyHack(5) ).at( 5, 7, 9 )
conq_dps.use( Bloodbath(6) ).at( 4, 8 )

# Abilities
conq_dps.use( BladeWeave() ).at( 1 )
conq_dps.use( UseDiscipline() ).at( 2 )
conq_dps.use( Annihilate() ).at( 3 )
conq_dps.use( RendFlesh() ).at( 4 )


def do_rotation(rotation, pause_key):
    generic.register_keybinds(rotation)

    print('Starting...')
    hk1 = keyboard.add_hotkey(pause_key, rotation.do_pause, args=[pause_key])

    logging.debug('Preparing to start')

    hk2 = keyboard.add_hotkey('*', rotation.end_destructive)
    r = threading.Timer(0.1, rotation.start)
    r.start()


def main():
    # Go to the Game
    generic._set_focus()
    global conq_dps
    # Set-up keyhooks
    try:
        #hk2 = keyboard.add_hotkey(80, start_rotation2, args=[grd_dps, 79])
        hk3 = keyboard.add_hotkey(81, do_rotation, args=[aggro, 79])
        hk4 = keyboard.add_hotkey(75, do_rotation, args=[conq_dps, 79])

        # Use this key to output the code for each key pressed. Makes it easier
        # to find new hotkeys.
        hk5 = keyboard.add_hotkey('-', generic.dump_keys)

        keyboard.wait('escape')
    except Exception as e:
        print(e)
    else:
        keyboard.unhook_all()
        generic._lose_focus()

if __name__ == "__main__":
    main()
