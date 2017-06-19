# gneral utltily
import logging
import time
import sched
import generic

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

from conqueror.combos import *


logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt = '%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)

r = Rotation()

generic.register_keybinds(r)

c = Whirlwind()
bb = Bloodbath(6)

r.use( c ).at()
r.use( bb ).at()



pyautogui.PAUSE = 0.1

def main():
    r.start()

main()
