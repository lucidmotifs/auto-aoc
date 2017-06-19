import time
import pyautogui
import datetime
import keyboard
import threading
import logging
from timeit import default_timer as timer


class COOLDOWN_ACTIONS:
    WAIT = 0
    SKIP = 1
    WAIT_SHORT = 2
    RETRY = 3
    TIMER = 4


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
    cooldown_fudge = 0.0
    # default CD action is to try again until the skill is off CD
    cooldown_action = COOLDOWN_ACTIONS.WAIT
    cast_time = 0.0
    duration = 0.0
    use_on_cooldown = False
    lastused = None
    modifier = None

    def __init__(self, name, hotkey, cooldown_time, cast_time=0, duration=0):
        setattr(self, 'name', name)
        setattr(self, 'cooldown_time', cooldown_time)
        setattr(self, 'cast_time', float(cast_time))
        setattr(self, 'duration', float(duration))

        self._hotkey = hotkey
        self.modifier = None
        self.register_hotkey()


    def hotkey():
        doc = "The hotkey property."
        def fget(self):
            return self._hotkey
        def fset(self, value):
            self._hotkey = value
            self.register_hotkey(None)
        def fdel(self):
            del self._hotkey
        return locals()
    hotkey = property(**hotkey())


    def init_cooldown(self, fudge=0.0):
        if not self.cooling_down:
            actual_cd = self.cooldown_time + fudge

            self.cooldown = threading.Timer(actual_cd, self.cooldown_end)
            self.cooldown.setDaemon(True)
            self.cooldown.start()
            self.lastused = self.cooldown_start = timer()
            self.cooling_down = True


    def deregister_hotkey(self):
        # remove any other action that currently has this hotkey
        try:
            keyboard.unhook_key(self.hotkey)
            print("Removing old bindings")
        except ValueError as e:
            #print(e)
            try:
                keyboard.remove_hotkey(self.modifier or '' + '+' + self.hotkey)
                print("Removing old bindings")
            except (ValueError,TypeError) as e:
                #print(e)
                pass

    def register_hotkey(self):
        self.deregister_hotkey()

        # register key hooks for logging based on hotkey + steps
        print("Adding keyboard hooks")
        if self.modifier:
            keyboard.add_hotkey(self.modifier + '+' + self.hotkey, \
                self.hotkey_pressed)
        else:
            keyboard.hook_key( self.hotkey, \
                lambda: self.hotkey_pressed() )

        logging.debug("Hotkey {} registered for {}".format(self.hotkey, self.name))


    def hotkey_pressed(self):
        # Make sure press was really for you.
        if keyboard.is_pressed('shift') or keyboard.is_pressed('ctrl'):
            if self.modifier and keyboard.is_pressed(self.modifier):
                all_good = True
            else:
                return

        # check for cooldown fail
        if self.cooling_down:
            print("Ability {} was used while still on cooldown. {}s remaining".\
                format(self.name, self.cooldown_remaining))

            if self.cooldown_action == COOLDOWN_ACTIONS.WAIT:
                print("We'll wait")
                retry = threading.Timer(self.cooldown_remaining, self.use)
                retry.start()
            elif self.cooldown_action == COOLDOWN_ACTIONS.RETRY:
                print("We'll be pushy")
                retry = threading.Timer(.3, self.use)
                retry.start()
            elif self.cooldown_action == COOLDOWN_ACTIONS.WAIT_SHORT:
                print("We'll wait a short while only")
                if self.cooldown_remaining < 2.2:
                    retry = threading.Timer(self.cooldown_remaining, self.use)
                    retry.start()
                else:
                    logging.debug("Skipping execution of {} due to cooldown ({}s)".\
                        format(self.name, self.cooldown_remaining))
            else:  # SKIP
                logging.debug("Skipping execution of {} due to cooldown ({}s)".\
                    format(self.name, self.cooldown_remaining))
        else:
            logging.debug("{} was activated. Last used: {}".\
                format(self.name, self.lastused or 'Never'))

    def use(self, lock=None):

        print("Using: {}".format( self.name ))

        if self.modifier:
            pyautogui.keyDown(self.modifier)
            time.sleep(.05)
            pyautogui.press(self.hotkey)
            time.sleep(.05)
            pyautogui.keyUp(self.modifier)
        else:
            pyautogui.press(self.hotkey)

        # If we're casting, pause.
        # this is a quick hack to make BV work - if its casting, it's a spell.
        if self.cast_time > 0:
            time.sleep(self.cast_time + .55)

        # start cooldown
        self.init_cooldown()


    # returns the recorded keyboard input events
    def get_events(self):
        pass

    @property
    def cooldown_remaining(self):
        if not self.cooling_down:
            return 0.0
        else:
            return round( self.cooldown_time - (timer() - self.lastused), 2 )


    def cooldown_end(self):
        self.cooling_down = False
        self.cooldown = None

        print("{0} is now off cooldown".format(self.name))

        if self.use_on_cooldown:
            self.use()


    def status(self):
        if self.cooling_down:
            status = "On Cooldown ({0}s remaining)".format( \
                self.cooldown_remaining )
        else:
            status = "Off Cooldown"

        print("{0} is {1}".format(self.name, status))
