from timeit import default_timer as timer
import threading
import pyautogui
import keyboard
import time
import logging

from ability import Ability
from ability import COOLDOWN_ACTIONS

ATTACK_INT_1HE = .65

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

        self.log_entries= []


    def record_swing(self, direction, key, step_at="not_given"):
        self.log_entries.append("We swung with an {0} from the {1} to complete the {2} combo (step:{3})".format(key, direction, self.name, step_at))


    def record_break(self, length, reason):
        self.log_entries.append("We took a break for {0} seconds for {1}".format(length, reason))


    def attach_prefinisher(self, ability):
        self.pre_finishers.append(ability)


    def attach_prefinishers(self, abilities):
        for a in abilities:
            self.attach_prefinisher(a)


    def do_weavein(self):

        self.press_hotkey()

        if self.was_weaved:
            self.do_step( next(self.steps_iter), "weavein", True )


    def do_step(self, step, log_data="normal", weavin=False):
        if self.step_delays and self.step_at in self.step_delays.key():
            self.do_stepdelay(self.step_at, self.step_delays[self.step_at])

        if weavin:
            self.record_break(.2, "weaving-in")
            time.sleep(.2)
        else:
            self.record_break(ATTACK_INT_1HE, "attack interval")
            time.sleep(ATTACK_INT_1HE)

        if self.step_at == len(self.steps)-1:
            self.do_prefinishers()
            self.record_swing( "finisher " + log_data, step, self.step_at)
            pyautogui.press(step)
        else:
            self.record_swing( "builder " + log_data, step, self.step_at)
            pyautogui.press(step)
            self.step_at += 1


    def do_stepdelay(self, step, delay):
        print("Delaying step {0} by {1} due to step delay command.".format(step, delay))
        self.record_break(delay)
        time.sleep(delay)


    def do_prefinishers(self):
        # check for pre-finisher buffs and use, this will delay the step slightly
        if len(self.pre_finishers) > 0:
            [x.use(x.on_cooldown) for x in self.pre_finishers if not x.cooling_down]


    def recover(self, duration, reason):
        self.record_break(round(duration, 2), reason)
        time.sleep(round(duration, 2))


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

        logging.debug( "Hotkey: {}".format('+'.join(self.hotkey)) )

        if len(self.hotkey) is 2:
            # uses modifier
            pyautogui.keyDown(self.hotkey[0])
            pyautogui.press(self.hotkey[1])
            pyautogui.keyUp(self.hotkey[0])
            self.record_swing("opener_1", self.hotkey)
        else:
            keyboard.send('+'.join(self.hotkey))
            self.record_swing("opener_2", self.hotkey)


    def execute(self, next_combo=None ):

        logging.debug( "[Combo: %s]\n" % self.name )

        print("Executing {0}".format(self.name))

        if not self.was_weaved:
            self.press_hotkey()
        else:
            self.record_break(ATTACK_INT_1HE, "post weavein")
            time.sleep(ATTACK_INT_1HE)

        while True:
            try:
                self.do_step( next(self.steps_iter) )
            except StopIteration as e:
                break

        # do post-skill (d stance or reckoning for e.g.)
        if self.post_ability is not None:
            if self.post_ability.cast_time > 0.0:
                next_combo.should_weave = False
            self.post_ability.use()


        if self.execute_time > 0.9 and next_combo is not None \
                                 and next_combo.should_weave is True:
            # allow finisher to start or further actions will interrupt
            next_combo.was_weaved = True
            next_combo.do_weavein()

            self.record_break(self.execute_time/2, "before weaving")
            time.sleep(self.execute_time/2)

            self.record_break( (self.execute_time/2) - .2, "after weaving")
            time.sleep(self.execute_time/2 - .2)
        else:
            # sleep for execute
            self.record_break(self.execute_time, "execution")
            time.sleep(self.execute_time)

        we_are_behind = False

        # long periods of long combos may cause us to get behind the game tick.
        # using a recovery break gets us back on track
        if we_are_behind:
            self.recover(self.execute_time * .1, "Recovery")

        logging.debug( " (wait: {:0.2f})\n".format(self.execute_time) )

        # start cooldown
        self.init_cooldown(self.cooldown_fudge)

        print("Finished executing {}".format(self.name))

        self.was_weaved = False
        self.steps_iter = iter(self.steps)

        [print(log) for log in self.log_entries]
        self.log_entries = []


    def cooldown_end(self):
        self.cooling_down = False
        self.cooldown = None

        print("Combo {0} is now off cooldown".format(self.name))


    def add_delay(self, step, delay):
        self.step_delays[step-1] = delay
