# gneral utltily
import logging
import random
import _globals
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
    filename='auto-aoc.log',
    filemode='w',
    level=logging.DEBUG)

_rotation = None
_rotationT = threading.Thread()


def reset():
    global _rotation
    _rotation.do_restart()


def begin(rotation, pause_key):
    global _rotation
    print('Starting roation...')

    hk1 = keyboard.add_hotkey(pause_key, rotation.do_pause)
    _rotation = rotation

    logging.debug('Preparing to start')
    _globals.register_keybinds(_rotation)

    hk2 = keyboard.add_hotkey('*', terminate)
    hk3 = keyboard.add_hotkey('+', reset)

    _rotationT = threading.Thread(target=_rotation.do_start)
    _rotationT.start()


def terminate():
    """End the currently running rotation"""
    global _rotation
    # cleart the current q
    # rotation should end gracefuilly
    _rotation.do_terminate()

def main():
    keyboard.unhook_all()

    # Go to the Game
    #generic._set_focus()
    guard_dps = Guardian_DPS()
    #guard_aggro = Guardian_Aggro()
    #conq_dps = Conqueror_DPS()
    #conq_dps = Conqueror_DPS()
    #blank = Rotation()
    #blank.ability_list.append( TacticProvoke() )
    #blank.ability_list.append( TacticDefense() )
    # Set-up keyhooks
    try:
        hk2 = keyboard.add_hotkey('up', begin, args=[guard_dps, '-'])
        #hk3 = keyboard.add_hotkey('left', begin, args=[guard_aggro, '-'])
        #hk4 = keyboard.add_hotkey('right', do_rotation, args=[conq_dps, 79])
        #hk5 = keyboard.add_hotkey('down', do_rotation, args=[blank, 79])

        # keys = input()
        print("Press escape to exit.")
        keyboard.wait('escape')
    except Exception as e:
        print(e)
    finally:
        keyboard.unhook_all()
        #generic._lose_focus()

if __name__ == "__main__":
    main()
