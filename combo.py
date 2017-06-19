from timeit import default_timer as timer
import threading
import pyautogui
import keyboard
import time
import logging
import sched
from copy import copy

from ability import Ability
from ability import COOLDOWN_ACTIONS

ATTACK_INT_1HE = .65
OPENER_WAIT = .3

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
    attack_interval = ATTACK_INT_1HE

    def __init__(self, name, hotkey, steps, cooldown_time, \
                 cast_time=0.0, post_ability=None):
        self.name = name
        self.steps = steps
        self.post_ability = post_ability
        self.cast_time = float(cast_time)
        self.cooldown_time = float(cooldown_time)
        self.hotkey = hotkey

        self.set_factory_defaults()


    def set_factory_defaults(self):
        # results
        self.word = ''
        self.modifier = None
        self.duration = 0.0
        self.finisher = []
        self.key_events = []
        self.pre_finishers = []
        self.post_finishers[]


    def register_hotkey(self, rotation):
        self.deregister_hotkey()

        # register key hooks for logging based on hotkey + steps
        print("Adding keyboard hooks")
        if self.modifier:
            keyboard.add_hotkey(
                self.modifier + '+' + self.hotkey, \
                self.hotkey_pressed, \
                args=[rotation])
        else:
            keyboard.hook_key(
                self.hotkey, \
                lambda: self.hotkey_pressed(rotation) )

        logging.debug( "Hotkey {} registered for {}".format( \
            self.hotkey, \
            self.name) )


    def hotkey_pressed(self, rotation):
        # Will do cooldown check, should always just skip
        super().hotkey_pressed()

        # Additional step to
        rotation.log_keypress(self)


    def opener(self):
        if self.modifier:
            pyautogui.keyDown(self.modifier)
            time.sleep(.05)
            pyautogui.press(self.hotkey)
            time.sleep(.05)
            pyautogui.keyUp(self.modifier)
        else:
            pyautogui.press(self.hotkey)


    # This replaces the 'build_word' functionality we previously
    # had as it ensures key presses happen exactly when they are
    # supposed to even when a step takes slightly too long to complete.
    def create_schedule(self):
        s = self.schedule = sched.scheduler(timer)
        t = 0

        # currently 0 would be right after the previous combo finishers
        # and after the round abilities have been fired.
        # In future, this schedule will be called just before the end
        # of the previous cast so opener and first step are buffered
        s.enter(t, 1, self.opener)

        # Do the steps uninteruppted
        for i,step in enumerate(self.steps):
            if i is 0:
                t = OPENER_WAIT
            else:
                t = self.attack_interval * (i+1)

            s.enter(t, 1, pyautogui.press, argument=(step,))

        # Finally do any pre-finisher abilities immeidately
        # afterwards before the last swing locks and combo executes.
        if self.pre_finishers:
            t = self.attack_interval * len(self.steps)

            for i,ability in enumerate(self.pre_finishers):
                s.enter(t, i+2, ability.use)

        # finally
        t = self.attack_interval * (len(self.steps)+1)
        s.enter(t, 1, self.init_cooldown)


    def attach_postfinisher(self, ability):
        self.post_finishers.append(ability)


    def attach_prefinisher(self, ability):
        self.pre_finishers.append(ability)
        self.build_word()


    def attach_prefinishers(self, abilities):
        for a in abilities:
            self.attach_prefinisher(a)


    def do_prefinishers(self):
        # check for pre-finisher buffs and use, this will delay the step slightly
        if len(self.pre_finishers) > 0:
            [x.use() for x in self.pre_finishers \
                if not x.cooling_down]

        # Keeping around this uneeded code because we'll use it later to
        # add these abilities to the abilities Queue


    def record(self, ke):
        self.key_events.append(ke)


    def build_word(self):
        self.word = ''
        self.finisher = []
        if self.pre_finishers:
            steps_c = copy(self.steps)
            self.finisher.append(steps_c.pop())
            for a in self.pre_finishers:
                # guess we're deciding that pre_finishers can't have modifiers?
                self.finisher.append(''.join(a.hotkey))

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
        debt = .4
        time.sleep(self.attack_interval - debt)

        # pyautogui.typewrite(self.word, ATTACK_INT_1HE)
        for i,char in enumerate(self.word):
            pyautogui.press(char)
            time.sleep(self.attack_interval + (i * .1) + debt)
            if debt > 0:
                debt = 0.0

        if self.finisher:
            pyautogui.press(self.finisher)
            time.sleep(debt + self.attack_interval + len(self.word) * .1)

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

        debt = .4
        print("Sleep for {}".format(self.attack_interval - debt))
        time.sleep(self.attack_interval - debt)

        for i,char in enumerate(self.word):
            #pyautogui.press(char)
            print("Press {}".format(char))
            print("Sleep for {}".format(debt + self.attack_interval + (i * .1)))
            time.sleep(debt + self.attack_interval + (i * .1))
            if debt > 0:
                debt = 0.0

        if self.finisher:
            #pyautogui.press(self.finisher)
            print("Press {}".format(self.finisher))
            print("Sleep for {}".format(self.attack_interval + len(self.word) * .1))
            time.sleep(self.attack_interval + len(self.word) * .1)


        duration = timer() - start
        print("Duration: {}".format(round(duration, 2)))


    def use(self, lock=None):
        if not self.schedule:
            self.create_schedule()

        self.schedule.run()
