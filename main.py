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

# pre-built rotations
from rotations import *


logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt = '%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)

_rotation = None

def begin(rotation, pause_key):

    print('Starting roation...')
    hk1 = keyboard.add_hotkey(pause_key, rotation.do_pause, args=[pause_key])

    logging.debug('Preparing to start')
    generic.register_keybinds(rotation)
    hk2 = keyboard.add_hotkey('*', rotation.end_destructive)
    r = threading.Thread(target=rotation.start)
    r.daemon = True
    r.start()


def terminate():
    """End the currently running rotation"""


def main():
    keyboard.unhook_all()

    # Go to the Game
    #generic._set_focus()
    #guard_dps = Guardian_DPS()
    guard_aggro = Guardian_Aggro()
    #conq_dps = Conqueror_DPS()
    #conq_dps = Conqueror_DPS()
    #blank = Rotation()
    #blank.ability_list.append( TacticProvoke() )
    #blank.ability_list.append( TacticDefense() )
    # Set-up keyhooks
    try:
        #hk2 = keyboard.add_hotkey('up', do_rotation, args=[guard_dps, 79])
        hk3 = keyboard.add_hotkey('left', do_rotation, args=[guard_aggro, 79])
        #hk4 = keyboard.add_hotkey('right', do_rotation, args=[conq_dps, 79])
        #hk5 = keyboard.add_hotkey('down', do_rotation, args=[blank, 79])

        #keys = input()
        keyboard.wait('escape')
    except Exception as e:
        print(e)
    finally:
        keyboard.unhook_all()
        #generic._lose_focus()

if __name__ == "__main__":
    main()
