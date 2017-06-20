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

    _schedule = sched.scheduler()

    cooldown_start = None
    cooldown_time = 0.0
    do_record = False
    lastused = None
    finisher = []
    pre_finishers = []
    post_finishers = []
    attack_interval = ATTACK_INT_1HE

    def __init__(self, name, cooldown_time=0.0, cast_time=0.0):
        super().__init__(name, cooldown_time, cast_time)
        self.factory()


    def factory(self):
        # initialize some properties to defaults. useful while developing,
        # but probably not needed moving forward.
        self.word = ''
        self.modifier = None
        self.duration = 0.0
        self.finisher = []
        self.key_events = []
        self.pre_finishers = []
        self.post_finishers = []


    def schedule():
        doc = "The schedule property."
        def fget(self):
            if not self._schedule or self._schedule.empty():
                self.create_schedule()
            return self._schedule
        def fset(self, value):
            self._schedule = value
        def fdel(self):
            del self._schedule
        return locals()
    schedule = property(**schedule())


    def register_hotkey(self, rotation):
        self.deregister_hotkey()

        # register key hooks for logging based on hotkey + steps
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
        s.enter(t, 1, self.activate)

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
        t = self.attack_interval * (len(self.steps)+1) + self.cast_time
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


    # ready to delete...
    def simulate_keyevents(self):
        self.use()

    # very similiar to simuulate, except every keypress because a print, and
    # all sleep and printed as well. continuing attempt to see if a combo will
    # work without running a manual test in-game.
    def print_keyevents(self):

        start = timer()

        ## will update for new scheduler system soon
        print(self.schedule.queue)


        duration = timer() - start
        print("Duration: {}".format(round(duration, 2)))


    def use(self, rotation=None):
        pyautogui.PAUSE = 0.05

        self.schedule.run()

        if self.post_finishers and rotation:
            
