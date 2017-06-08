import time
import pyautogui
import pywinauto
import datetime
import keyboard
import threading
import logging
from timeit import default_timer as timer


class COOLDOWN_ACTIONS:
    WAIT = 0
    SKIP = 1
    TIMER = 2


""" Abilities are spells or buffs that are cast at one of the following times:
    - Before the start of a combo, because the character requires the effect immmediately.
    - Right before the Finisher is pressed as the buffs need only apply to execution.
    - After the combo finishes, such as reckoning"""
class Ability(object):

    name = ""
    cooldown = None
    cooling_down = False
    cooldown_time = 0.0
    last_actual_cooldown = 0.0
    cooldown_fudge = 0.35
    # default CD action is to try again until the skill is off CD
    cooldown_action = COOLDOWN_ACTIONS.WAIT
    cast_time = 0.0
    duration = 0.0
    on_cooldown = False
    lastused = None

    def __init__(self, name, hotkey, cooldown_time, cast_time=0, duration=0):
        setattr(self, 'name', name)
        setattr(self, 'cooldown_time', cooldown_time)
        setattr(self, 'cast_time', float(cast_time))
        setattr(self, 'duration', float(duration))

        self.hotkey = hotkey # register this properly with keyboard module


    def init_cooldown(self, fudge=0.0):
        if not self.cooling_down:
            if self.cooldown_time - fudge < 1:
                actual_cd = 1
            else:
                actual_cd = self.cooldown_time - fudge

            self.cooldown = threading.Timer(actual_cd, self.cooldown_end)
            self.cooldown.start()
            self.lastused = self.cooldown_start = timer()
            self.cooling_down = True


    def use(self, on_cooldown=False):

        print("Using: {0}".format(self.name))

        if len(self.hotkey) is 2:
            # uses modifier
            pyautogui.keyDown(self.hotkey[0])
            pyautogui.press(self.hotkey[1])
            pyautogui.keyUp(self.hotkey[0])
        else:
            keyboard.send('+'.join(self.hotkey))
            #pyautogui.press(self.hotkey[0])

        print(self.hotkey)

        # If we're casting, pause.
        if self.cast_time > 0:
            time.sleep(self.cast_time)

        # start cooldown
        self.init_cooldown(self.cooldown_fudge)

        # create timer if we want to use this ability everytime it's up.


    def cooldown_remaining(self):
        if not self.cooling_down:
            return 0.0
        else:
            return round( self.cooldown_fudge + self.cooldown_time - \
                            (timer() - self.lastused), 2 )


    def cooldown_end(self):
        self.on_cooldown = False
        self.cooling_down = False
        self.cooldown = None


    def status(self):
        if self.cooling_down:
            status = "On Cooldown ({0}s remaining)".format( \
                self.cooldown_remaining() )
        else:
            status = "Off Cooldown"

        print("{0} is {1}".format(self.name, status))
