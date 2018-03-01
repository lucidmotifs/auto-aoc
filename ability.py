import time
import pyautogui
import datetime
import keyboard
import threading
import logging
import _globals
from timeit import default_timer as timer


class cooldown_actions:
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

    cooling_down = False
    cooldown_time = 0.0
    cast_time = 0.0
    duration = 0.0
    lastused = None

    # default CD action is to try again until the skill is off CD
    cooldown_action = cooldown_actions.SKIP

    # use ability immmediately when CD comes up
    use_on_cooldown = False

    # modifier key for hotkeys
    modifier = None

    # global combat instance
    _combat = None


    def __init__(self, name="", cooldown_time=0, cast_time=0, duration=0):
        setattr(self, 'name', name)
        setattr(self, 'cooldown_time', cooldown_time)
        setattr(self, 'cast_time', float(cast_time))
        setattr(self, 'duration', float(duration))

        # event comfirming the ability was successfully activated.
        self._key_pressed = threading.Event()

        # cooldown timer thread
        self.cooldown = threading.Timer(self.cooldown_time, self.cooldown_end)


    def hotkey():
        doc = "The hotkey property."
        def fget(self):
            return self._hotkey
        def fset(self, value):
            self._hotkey = value
            self.register_hotkey()
        def fdel(self):
            del self._hotkey
        return locals()
    hotkey = property(**hotkey())

    def combat():
        doc = "The combat singleton."
        def fget(self):
            return self._combat
        def fset(self, value):
            self._combat = value
        def fdel(self):
            del self._combat
        return locals()
    combat = property(**combat())


    @property
    def cooling_down(self):
        return self.cooldown.is_alive()


    def init_cooldown(self, fudge=0.0):
        if not self.cooling_down:
            actual_cd = self.cooldown_time + fudge

            if actual_cd > 0.0:
                self.cooldown.start()

            self.lastused = self.cooldown_start = timer()

    @property
    def cooldown_remaining(self):
        """Returns the amount of time until an ability is off cooldown"""
        if not self.cooling_down:
            return 0.0
        else:
            return round( self.cooldown_time - (timer() - self.lastused), 2 )


    def cooldown_end(self):
        logging.debug("{0} is now off cooldown".format(self.name))

        # reset the cooldown timer
        del self.cooldown
        self.cooldown = threading.Timer(self.cooldown_time, self.cooldown_end)

        if self.use_on_cooldown:
            time.sleep(.1)
            self.use()


    def deregister_hotkey(self):
        """Remove any other action that currently has this hotkey"""
        try:
            if self.modifier:
                keyboard.remove_hotkey(self.modifier + '+' + self.hotkey)
                _hotkey = self.modifier + '+' + self.hotkey
            else:
                keyboard.unhook_key( self.hotkey, )
                _hotkey = self.hotkey
        except Exception as e:
            return

        logging.debug("Hotkey {} de-registered for {}".format(_hotkey, \
                                                              self.name))

    def register_hotkey(self):
        self.deregister_hotkey()

        # register key hooks for logging based on hotkey + steps
        if self.modifier:
            keyboard.add_hotkey(
                self.modifier + '+' + self.hotkey, \
                self.hotkey_pressed)
        else:
            keyboard.hook_key(
                self.hotkey, \
                lambda: self.hotkey_pressed() )

        logging.debug( "Hotkey {} registered for {}".format( \
            self.hotkey, \
            self.name) )


    # Returns true if and only if we have finished trying, not if the
    # press 'happened' - we're here because it deciding-
    def hotkey_pressed(self):
        from world import World

        self._pressed = self._key_pressed.is_set()

        # Make sure press was really for this ability.
        if keyboard.is_pressed('shift') or keyboard.is_pressed('ctrl'):
            # ensure the modifier key currently being held
            if not self.modifier or not keyboard.is_pressed(self.modifier):
                self._pressed = False
            else:
                self._pressed = True
        elif self.modifier:
            self._pressed = False
        else:
            self._pressed = True

        # Set hotkey event as pressed
        self._key_pressed.set()

        # Additional step to pass event to rotation
        if self._pressed:
            _globals.log_keypress(self.hotkey,
                "Hotkey for {} pressed".format(self.name),
                World._current_action)


    def cooldown_check(self):
        # check for cooldown fail
        if self.cooling_down:

            logging.debug(
                "Ability {} was used while still on cooldown. {}s remaining".\
                format(self.name, self.cooldown_remaining))

            if self.cooldown_action == cooldown_actions.WAIT:
                logging.info("On Cool-down action was WAIT, waiting.")
                retry = threading.Timer(self.cooldown_remaining,
                                        self.use).start()
            elif self.cooldown_action == cooldown_actions.RETRY:
                logging.info("On Cool-down action was RETRY, retrying.")
                retry = threading.Timer(1, self.use).start()
            elif self.cooldown_action == cooldown_actions.WAIT_SHORT:
                logging.info("On Cool-down action was WAIT_SHORT, waiting a \
                short while")
                if self.cooldown_remaining < 3:
                    retry = threading.Timer(self.cooldown_remaining,
                                            self.use).start()
                else:
                    logging.info( \
                        "Skipping execution of {} due to cooldown ({}s)". \
                        format(self.name, self.cooldown_remaining))

            else:  # SKIP
                logging.info( \
                    "Skipping execution of {} due to cooldown ({}s)". \
                    format(self.name, self.cooldown_remaining))

            return False
        else:
            logging.debug("{} was activated. Last used: {}". \
                          format(self.name, self.lastused or 'Never'))

            return True


    # press the button.
    def activate(self):
        self._key_pressed.clear()

        if self.modifier:
            pyautogui.keyDown(self.modifier)
            time.sleep(.05)
            pyautogui.press(self.hotkey)
            time.sleep(.05)
            pyautogui.keyUp(self.modifier)
        else:
            pyautogui.press(self.hotkey)


    def use(self, combat=None):
        """ Peform the actions required to fire the ability """
        # return immeidately if cooldown_check fails
        if not self.cooldown_check():
            return

        logging.debug("Using: {}".format( self.name ))

        if combat:
            logging.debug("Setting exec lock to run {}".format(self.name))
            combat.exec_lock.acquire()

        self.activate()

        # Wait for allowed event
        if self._key_pressed.wait(5):
            # key press, not timeout.
            if self._pressed:
                # If we're casting, pause.
                # this is a quick hack to make BV work - if its casting, it's a spell.
                if self.cast_time > 0:
                    time.sleep(self.cast_time)

                # start cooldown
                self.init_cooldown()
        else:
            message = "Error: Timeout reach while waiting for {}" \
                       .format(self.name)
            logging.error( message )

            if combat:
                logging.debug("Releasing exec lock for {}".format(self.name))
                combat.exec_lock.release()

            # waiting for a timeout this long means something
            # is really broken with out system or our Rotation
            # and we should exit. decide on action later
            return

        if combat:
            logging.debug("Releasing exec lock for {}".format(self.name))
            combat.exec_lock.release()


    # returns the recorded keyboard input events
    def get_events(self):
        pass


    def status(self):
        if self.cooling_down:
            status = "On Cooldown ({0}s remaining)".format( \
                self.cooldown_remaining )
        else:
            status = "Off Cooldown"

        logging.debug("{0} is {1}".format(self.name, status))


    @property
    def word(self):
        return self.hotkey
