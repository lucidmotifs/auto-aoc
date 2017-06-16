from timeit import default_timer as timer
import threading
import pyautogui
import keyboard
import time
import logging
from copy import copy

from ability import Ability
from ability import COOLDOWN_ACTIONS

ATTACK_INT_1HE = .65
OPENER_WAIT = .1

DEBUG = False

class Combo(Ability):

    cooldown = None
    cooldown_start = None
    cooldown_time = 0.0
    cooling_down = False
    do_record = False
    lastused = None
    finisher = []
    pre_finishers = []
    post_ability = None
    duration = 0.0

    def __init__(self, name, hotkey, steps, cooldown_time, \
                 cast_time=0.0, post_ability=None):
        self.name = name
        self.steps = steps
        self.post_ability = post_ability
        self.cast_time = float(cast_time)
        self.cooldown_time = float(cooldown_time)
        self.hotkey = hotkey
        self.step_delays = {}
        self.pre_finishers = []

        self.set_factory_defaults()


    def set_factory_defaults(self):
        # results
        self.word = ''
        self.modifier = None
        self.duration = 0.0
        self.finisher = []
        self.key_events = []


    def register_hotkey(self, rotation):
        self.deregister_hotkey()

        # register key hooks for logging based on hotkey + steps
        print("Adding keyboard hooks")
        if self.modifier:
            keyboard.add_hotkey(self.modifier + '+' + self.hotkey, \
                self.hotkey_pressed)
        else:
            keyboard.hook_key( self.hotkey, \
                lambda: self.hotkey_pressed(rotation) )

        logging.debug("Hotkey {} registered for {}".format(self.hotkey, self.name))


    def hotkey_pressed(self, rotation):
        super().hotkey_pressed()

        # Additional step to
        rotation.log_keypress(self)

    def attach_prefinisher(self, ability):
        self.pre_finishers.append(ability)


    def attach_prefinishers(self, abilities):
        for a in abilities:
            self.attach_prefinisher(a)


    def do_stepdelay(self, step, delay):
        print("Delaying step {0} by {1} due to step delay command.".format(step, delay))
        time.sleep(delay)


    def do_prefinishers(self):
        # check for pre-finisher buffs and use, this will delay the step slightly
        if len(self.pre_finishers) > 0:
            [x.use(x.on_cooldown) for x in self.pre_finishers \
                if not x.cooling_down]


    def record(self, ke):
        self.key_events.append(ke)


    def build_word(self):
        self.word = ''
        if hasattr(self, 'pre_finishers') and self.pre_finishers:
            for a in self.pre_finishers:
                self.finisher.append(''.join(a.hotkey))
            steps_c = copy(self.steps)
            self.finisher.append(steps_c.pop())
            self.word += ''.join(steps_c)
        else:
            self.word += ''.join(self.steps)


    def simluate_keyevents(self):
        # check cooldown
        # create 'word'
        # time word execution
        # subtract tick difference from final wait time
        # do all computation before sending the word!
        # this should ensure each key_press is sent in good time.
        ATTACK_INT_1HE = .65

        pyautogui.PAUSE = 0.0

        if self.word is None:
            self.build_word()

        start = timer()

        # do_opener()
        if self.modifier:
            pyautogui.keyDown(self.modifier)
            time.sleep(.05)
            pyautogui.press(self.hotkey)
            time.sleep(.05)
            pyautogui.keyUp(self.modifier)
        else:
            pyautogui.press(self.hotkey)
            time.sleep(.1)

        # we sleep after opener even though we could lock it.
        # would be great to have a v2 of this method that buffers input by ends
        # up with the same timing overall (no missed combos) and see if buffering
        # is an advantage (i think it is because lag - no buffering is constant .1)
        # loss, which is why we are constantly adding .1 to things...and when i get pausing
        # spike, combos are missed.
        time.sleep(self.attack_interval)

        # pyautogui.typewrite(self.word, ATTACK_INT_1HE)
        for i,char in enumerate(self.word):
            pyautogui.press(char)
            time.sleep(self.attack_interval + ((i+1) * .1))

        if self.finisher:
            time.sleep(self.attack_interval + len(self.word) * .1)
            pyautogui.press(self.finisher)

        end = timer()

        # timeit
        actual = end - start

        expected = (len(self.steps) + 1) * self.attack_interval

        if len(self.finisher) > 0:
            expected += self.attack_interval

        wait_more =  round((actual - expected) / 6, 2)

        # calculate time to wait for casting
        pause = self.cast_time + wait_more
        logging.debug("cast time: {}".format( pause ))
        logging.debug("actual {} vs expected {}".format( round(actual, 2), \
            round(expected, 2) ))
        logging.debug("wait more time: {}".format(wait_more))
        time.sleep( pause )

        # do post ability, use keyboard to avoid long delays
        #if self.post_ability:
        #    keyboard.send(self.post_ability.hotkey)

        self.duration = timer() - start

        self.init_cooldown()

    # very similiar to simuulate, except every keypress because a print, and
    # all sleep and printed as well. continuing attempt to see if a combo will
    # work without running a manual test in-game.
    def print_keyevents(self):

        start = timer()

        # do_opener()
        if self.modifier:
            #pyautogui.keyDown(self.modifier)
            print("keyDown {}".format(self.modifier))
            print("sleep .05")
            time.sleep(.05)
            #pyautogui.press(self.hotkey)
            print("Press {}".format(self.hotkey))
            print("sleep .05")
            time.sleep(.05)

            #pyautogui.keyUp(self.modifier)
            print("keyUp {}".format(self.modifier))
        else:
            #pyautogui.press(self.hotkey)
            print("Press {}".format(self.hotkey))
            print("sleep .1")
            time.sleep(.1)

        print("Sleep for {}".format(self.attack_interval))
        time.sleep(self.attack_interval)

        # pyautogui.typewrite(self.word, ATTACK_INT_1HE)
        for i,char in enumerate(self.word):
            #pyautogui.press(char)
            print("Press {}".format(char))
            print("Sleep for {}".format(self.attack_interval + ((i+1) * .1)))
            time.sleep(self.attack_interval + ((i+1) * .1))

        if self.finisher:
            print("Sleep for {}".format(self.attack_interval + len(self.word) * .1))
            time.sleep(self.attack_interval + len(self.word) * .1)
            #pyautogui.press(self.finisher)
            print("Press {}".format(self.finisher))

        duration = timer() - start
        print("Duration: {}".format(round(duration, 2)))


    def add_delay(self, step, delay):
        self.step_delays[step-1] = delay
