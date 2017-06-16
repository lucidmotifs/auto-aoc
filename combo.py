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

    was_weaved = False
    should_weave = False
    cooldown = None
    cooldown_start = None
    cooldown_time = 0.0
    cooling_down = False
    do_record = False
    lastused = None

    def __init__(self, name, hotkey, steps, cooldown_time, \
                 cast_time=0.0, post_ability=None):
        self.name = name
        self.steps = steps
        self.post_ability = post_ability
        self.cast_time = float(cast_time)
        self.cooldown_time = float(cooldown_time)
        self.hotkey = property(**hotkey())
        self.step_delays = {}
        self.pre_finishers = []

        # step counting
        self.steps_iter = iter(self.steps)
        self.step_at = 0

        # results
        self.word = ''
        self.modifier = None
        self.finisher = []
        self.duration = 0.0
        self.key_events = []


    def hotkey():
        doc = "The hotkey property."
        def fget(self):
            return self._hotkey
        def fset(self, value):
            self._hotkey = value
        def fdel(self):
            del self._hotkey
        return locals()


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
        if len(self.pre_finishers) > 0:
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
        pyautogui.PAUSE = 0.3

        if DEBUG:
            pyautogui.press('enter')
            pyautogui.typewrite(self.name)
            pyautogui.press('enter')

            time.sleep(3)

        pyautogui.PAUSE = 0.0

        if self.word is None:
            self.build_word()

        start = timer()

        if self.modifier:
            pyautogui.keyDown(self.modifier)
            time.sleep(.05)
            pyautogui.press(self.hotkey)
            time.sleep(.05)
            pyautogui.keyUp(self.modifier)
        else:
            pyautogui.press(self.hotkey)
            time.sleep(.1)

        #pyautogui.press(self.hotkey)

        time.sleep(ATTACK_INT_1HE)

        # pyautogui.typewrite(self.word, ATTACK_INT_1HE)
        for i,char in enumerate(self.word):
            pyautogui.press(char)
            time.sleep(ATTACK_INT_1HE + ((i+1) * .1))

        if len(self.finisher) > 0:
            time.sleep(ATTACK_INT_1HE + len(self.word) * .1)
            pyautogui.press(self.finisher)

        end = timer()

        # timeit
        actual = end - start

        expected = (len(self.steps) + 1) * ATTACK_INT_1HE

        if len(self.finisher) > 0:
            expected += ATTACK_INT_1HE

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


    def cooldown_end(self):
        self.cooling_down = False
        self.cooldown = None

        print("Combo {0} is now off cooldown".format(self.name))


    def add_delay(self, step, delay):
        self.step_delays[step-1] = delay
