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
    #generic._set_focus()
    guard_aggro = Guardian_Aggro()
    conq_dps = Conqueror_DPS()
    # Set-up keyhooks
    try:
        #hk2 = keyboard.add_hotkey(80, start_rotation2, args=[grd_dps, 79])
        hk3 = keyboard.add_hotkey(81, do_rotation, args=[guard_aggro, 79])
        hk4 = keyboard.add_hotkey(75, do_rotation, args=[conq_dps, 79])

        # Use this key to output the code for each key pressed. Makes it easier
        # to find new hotkeys.
        #hk5 = keyboard.add_hotkey('-', generic.dump_keys)

        keyboard.wait('escape')
    except Exception as e:
        print(e)
    else:
        keyboard.unhook_all()
        #generic._lose_focus()

if __name__ == "__main__":
    main()
