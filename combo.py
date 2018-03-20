from timeit import default_timer as timer
import threading
import pyautogui
import keyboard
import time
import logging
import sched
from copy import copy

import _globals
from ability import Ability
from ability import cooldown_actions
from world import World


class Combo(Ability):

    cooldown_start = None
    cooldown_time = 0.0
    do_record = False
    lastused = None
    finisher = []
    pre_finishers = []
    post_finishers = []
    attack_interval = _globals.attack_int_1he

    def __init__(self, name, cooldown_time=0.0, cast_time=0.0):
        super().__init__(name, cooldown_time, cast_time)
        self.factory()

    def factory(self):
        # initialize some properties to defaults. useful while developing,
        # but probably not needed moving forward.
        self.modifier = None
        self.duration = 0.0
        self.finisher = []
        self.key_events = []
        self.pre_finishers = []
        self.post_finishers = []
        self._schedule = sched.scheduler()

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

    def rotation():
        doc = "The rotation property."
        def fget(self):
            return self._rotation
        def fset(self, value):
            self._rotation = value

            # set the rotation for all pre/post finishers
            if self.pre_finishers:
                for a in self.pre_finishers:
                    a.rotation = value
            if self.post_finishers:
                for a in self.post_finishers:
                    a.rotation = value
        def fdel(self):
            del self._rotation
        return locals()
    rotation = property(**rotation())

    # This replaces the 'build_word' functionality we previously
    # had as it ensures key presses happen exactly when they are
    # supposed to even when a step takes slightly too long to complete.
    def create_schedule(self):
        logging.debug("Creating Schedule for {}".format(self.name))
        s = self.schedule = sched.scheduler(timer)
        t = 0.0

        # currently 0 would be right after the previous combo finishers
        # and after the round abilities have been fired.
        # In future, this schedule will be called just before the end
        # of the previous cast so opener and first step are buffered
        s.enter(t, 1, self.activate)

        # Do the steps uninteruppted
        for i,step in enumerate(self.steps):
            if i is 0:
                t = _globals.attack_int_override or _globals.opener_wait
            else:
                t = self.attack_interval * (i+1)

            s.enter(t, 1, pyautogui.press, argument=(step,))

        # Do any pre-finisher abilities immeidately
        # afterwards before the last swing locks and combo executes.
        if self.pre_finishers:
            t = self.attack_interval * len(self.steps)

            for i,ability in enumerate(self.pre_finishers):
                s.enter(t, i+2, ability.use)

        # finally
        t = (self.attack_interval * \
            (len(self.steps)+1) + self.cast_time + 0.1)
        s.enter(t, 1, self.init_cooldown)

        return self.schedule.queue

    def attach_postfinisher(self, ability):
        self.post_finishers.append(ability)

    def attach_prefinisher(self, ability):
        self.pre_finishers.append(ability)

    def attach_prefinishers(self, abilities):
        for a in abilities:
            self.attach_prefinisher(a)

    def do_prefinishers(self):
        # check for pre-finisher buffs and use, this will delay the step slightly
        if len(self.pre_finishers) > 0:
            [x.use() for x in self.pre_finishers \
                if not x.cooling_down]

    def record(self, ke):
        self.key_events.append(ke)

    @property
    def word(self):
        # start with
        self._word = list(super().word)

        [self._word.append(s) for s in self.steps]
        [self._word.append(''.join(a.word)) for a in self.pre_finishers
            if self.pre_finishers]
        [self._word.append(''.join(a.word)) for a in self.post_finishers
            if self.post_finishers]

        return ''.join(self._word)


    # ready to delete...
    def simulate_keyevents(self):
        self.use()

    # very similiar to simulate, except every keypress because a print, and
    # all sleep and printed as well. continuing attempt to see if a combo will
    # work without running a manual test in-game.
    def print_keyevents(self):
        ## will update for new scheduler system soon
        logging.debug(self.schedule.queue)


    def use(self, rotation=None):
        """ Peform the actions required to fire the ability """
        # return immeidately if cooldown_check fails
        if not self.cooldown_check():
            return

        pyautogui.PAUSE = 0.05

        self.schedule.run()

        if self.post_finishers and rotation:
            for a in self.post_finishers:
                # guess we're deciding that pre_finishers can't have modifiers?
                rotation.ability_q.put(a)
