# gneral utltily
import logging
import time
import sched

# keyboard hooks
import keyboard
import pyautogui

# timing module
from timeit import default_timer as timer

# from this application
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


s = sched.scheduler(timer, time.sleep)
c = Whirlwind()
bb = Bloodbath(6)

pyautogui.PAUSE = 0.1

def schedule():
    s.enter(0, 1, pyautogui.press, argument=(c.hotkey,))
    s.enter(0, 2, logging.debug, argument=(c.hotkey,))

    s.enter(0.3, 1, pyautogui.press, argument=(c.steps[0],))
    s.enter(0.3, 2, logging.debug, argument=(c.steps[0],))

    s.enter(1.3, 1, pyautogui.press, argument=(c.steps[1],))
    s.enter(1.3, 2, logging.debug, argument=(c.steps[1],))

    s.enter(1.95, 1, pyautogui.press, argument=(c.steps[2],))
    s.enter(1.95, 2, logging.debug, argument=(c.steps[2],))

    s.enter(4.1, 1, logging.debug, argument=(bb.hotkey,))
    s.enter(4.5, 1, logging.debug, argument=(bb.steps[0],))
    s.enter(5.4, 1, logging.debug, argument=(bb.steps[1],))
    s.enter(6.05, 1, logging.debug, argument=(bb.steps[2],))

    s.run()


schedule()
