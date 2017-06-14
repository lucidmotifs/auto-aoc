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

class Combo(Ability):

    was_weaved = False
    should_weave = False
    cooldown = None
    cooldown_start = None
    cooldown_time = 0.0
    cooling_down = False
    lastused = None

    def __init__(self, name, hotkey, steps, cooldown_time, \
                 execute_time=0.0, post_ability=None):
        self.name = name
        self.hotkey = hotkey
        self.steps = steps
        self.post_ability = post_ability
        self.execute_time = float(execute_time)
        self.cooldown_time = float(cooldown_time)
        self.step_delays = {}
        self.pre_finishers = []

        # step counting
        self.steps_iter = iter(self.steps)
        self.step_at = 0

        # results
        self.modifier = None
        self.word = None
        self.finisher = []
        self.duration = 0.0
        self.events = None


    def attach_prefinisher(self, ability):
        self.pre_finishers.append(ability)


    def attach_prefinishers(self, abilities):
        for a in abilities:
            self.attach_prefinisher(a)


    def do_weavein(self):

        self.press_hotkey()

        #if self.was_weaved:
            #self.do_step( next(self.steps_iter), "weavein", True )


    def do_step(self, step, log_data="normal", weavein=False):
        if self.step_delays and self.step_at in self.step_delays.keys():
            self.do_stepdelay(self.step_at, self.step_delays[self.step_at])

        if weavein or self.step_at == 0:
            # time.sleep( .1 )
            time.sleep(ATTACK_INT_1HE)
        elif self.step_at == 1:
            time.sleep( ATTACK_INT_1HE )
        else:
            time.sleep(ATTACK_INT_1HE)

        if self.step_at == len(self.steps)-1:
            self.do_prefinishers()
            pyautogui.press(step)
        else:
            pyautogui.press(step)

        self.step_at += 1


    def do_stepdelay(self, step, delay):
        print("Delaying step {0} by {1} due to step delay command.".format(step, delay))
        time.sleep(delay)


    def do_prefinishers(self):
        # check for pre-finisher buffs and use, this will delay the step slightly
        if len(self.pre_finishers) > 0:
            [x.use(x.on_cooldown) for x in self.pre_finishers \
                if not x.cooling_down]


    def record(self):
        print("recording...please don't touch the keyboard")
        t = threading.Timer(1, self.go)
        t.start()

        self.events = keyboard.record(until='/')


    def build_word(self):
        self.word = ""
        if len(self.pre_finishers) > 0:
            for a in self.pre_finishers:
                self.finisher.append(''.join(a.hotkey))
            steps_c = copy(self.steps)
            self.finisher.append(steps_c.pop())
            self.word += ''.join(steps_c)
        else:
            self.word += ''.join(self.steps)


    def go(self):
        # check cooldown
        # create 'word'
        # time word execution
        # subtract tick difference from final wait time
        # do all computation before sending the word!
        # this should ensure each key_press is sent in good time.
        pyautogui.PAUSE = .65

        if self.word is None:
            self.build_word()

        #print(', '.join(self.hotkey))
        #print(self.word)
        #print(self.finisher)

        start = timer()
        pyautogui.hotkey(*self.hotkey)
        opener = timer()
        logging.debug("opener: {}".format( opener-start ))
        pyautogui.typewrite(self.word, .65)
        steps = timer()
        logging.debug("steps: {}".format(steps - opener))
        if len(self.finisher) > 0:
            pyautogui.press(self.finisher)
        end = timer()
        logging.debug("finisher: {}".format( end - steps ))

        time.sleep(self.execute_time)
        pyautogui.typewrite("/")
        self.init_cooldown()
        actual = end - start
        expected = (len(self.steps) + 1) * .65
        wait_less = actual - expected
        logging.debug("actual {} vs expected {}".format(round(actual, 2), \
            round(expected, 2)))

        self.duration = actual


    def press_hotkey(self):

        if self.cooling_down:
            # record error
            print("Skill: %s was used while still on CD" % self.name)
            print("{0:0.2f} seconds left on CD last used at {1:0.2f}".format(self.cooldown_remaining(), self.cooldown_start))

            if self.was_weaved:
                self.was_weaved = False
                return
            elif self.cooldown_action is COOLDOWN_ACTIONS.WAIT:
                time.sleep( self.cooldown_remaining() + self.cooldown_fudge )
                return self.press_hotkey()
            elif self.cooldown_action is COOLDOWN_ACTIONS.SKIP:
                print( "Skill: {0} was skipped as it was still on CD".format(self.name) )

        elif self.lastused is not None:
            cooldown_expired = (timer() - self.lastused) - self.cooldown_time
            print("Skill: {0} was used {1:0.2f} seconds after CD expired".format(self.name, cooldown_expired))

        if len(self.hotkey) is 2:
            # uses modifier
            pyautogui.keyDown(self.hotkey[0])
            pyautogui.press(self.hotkey[1])
            pyautogui.keyUp(self.hotkey[0])
        else:
            keyboard.send('+'.join(self.hotkey))


    def execute(self, next_combo=None ):

        print("Starting {0}".format(self.name))

        if not self.was_weaved:
            self.press_hotkey()

        while True:
            try:
                self.do_step( next(self.steps_iter) )
            except StopIteration as e:
                time.sleep(ATTACK_INT_1HE)
                breakR

        logging.debug( "Combo {} finished, waiting casttime (wait: {:0.2f})\n".format(self.name, self.execute_time) )

        if self.post_ability is not None and next_combo is not None:
            if self.post_ability.cast_time > 0.0:
                next_combo.should_weave = False

        if next_combo is not None:
            next_combo.should_weave = False

        if self.execute_time > 0.9 and next_combo is not None \
                                 and next_combo.should_weave is True:

            # allow finisher to start or further actions will interrupt
            time.sleep(self.execute_time - .1)

            next_combo.was_weaved = True
            next_combo.do_weavein()
        else:
            # sleep for execute
            time.sleep(self.execute_time)

        # switch stance right as castbar ends
        # pyautogui.press('z')

        # start cooldown
        self.init_cooldown(self.cooldown_fudge)

        # short recovery
        time.sleep(.1)

        if self.post_ability is not None:
            self.post_ability.use()

        print("Finished executing {}".format(self.name))

        self.was_weaved = False
        self.step_at = 0
        self.steps_iter = iter(self.steps)


    def cooldown_end(self):
        self.cooling_down = False
        self.cooldown = None

        print("Combo {0} is now off cooldown".format(self.name))


    def add_delay(self, step, delay):
        self.step_delays[step-1] = delay
