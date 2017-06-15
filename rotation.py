import time
import pyautogui
import pywinauto
import datetime
import keyboard
import threading
import logging
from timeit import default_timer as timer
from sortedcontainers import SortedDict
from pywinauto import application
from copy import copy

# from this application
from combo import Combo
from ability import Ability

class Rotation(object):

    def __init__(self):
        self.combo_list = []
        self.ability_list = []
        self.actions = SortedDict()
        self.repeat = False
        self.repeat_count = 0
        self.repeat_until = None
        self.unpause_key = None
        self.paused = False
        self.current_action = None
        self.last_keypress = 0.0

        # timers
        self.start_time = 0.0
        self.end_time = 0.0

        self._inprogress = False


    def do_resume(self):
        if self.unpause_key is not None:
            keyboard.remove_hotkey(self.unpause_key)

            print("waiting to resume...")
            keyboard.wait(self.unpause_key)

            print("resuming...")
            self.paused = False
            # change activation
            keyboard.add_hotkey(self.unpause_key, self.do_pause, args=[self.unpause_key])


    def do_pause(self, key_pressed):
        # pause the rotation in place, but allow CDs to finish (CDs in threads)
        # 'save state'
        print("pausing...")

        if not self.paused:
            self.paused = True
            self.unpause_key = key_pressed


    def register_hotkey(self, action):
        # remove any other action that currently has this hotkey
        try:
            keyboard.unhook_key(action.hotkey)
        except ValueError:
            try:
                keyboard.remove_hotkey(action.modifier + '+' + action.hotkey)
            except (ValueError,TypeError) as e:
                print(e)

        # register key hooks for logging based on hotkey + steps
        if action.modifier:
            keyboard.add_hotkey(action.modifier + '+' + action.hotkey, \
                self.log_keypress, \
                args=["Hotkey for {0} was pressed with modifier".format(action.name)])
        else:
            keyboard.hook_key( action.hotkey, \
                lambda: self.log_keypress(action) )

        logging.debug("Hotkey {} registered for {}".format('+'.join(action.hotkey), action.name))


    def log_keypress(self, message=None):
        if isinstance(message, Combo):
            msg = "Hotkey for {} was pressed".format(message.name)
        else:
            msg = message
        curr_time = timer()
        delta = curr_time - self.last_keypress
        logging.debug("During {}, {} ({})".format(self.current_action.name, \
            msg,
            round(timer(), 2)))
        logging.debug("Delta: {}".format(delta))
        self.last_keypress = curr_time


    def add(self, action_l):
        for action in action_l:
            if isinstance(action, Combo):
                self.add_combo( action )
            elif type(action) is Ability:
                self.add_ability( action )


    def add_combo(self, combo, positions=()):
        self.register_hotkey(combo)
        # copy the combo so it can modified
        combo_copy = copy(combo)

        if combo_copy not in self.combo_list:
            idx = len(self.combo_list)
            self.combo_list.append( combo_copy )
        else:
            idx = self.combo_list.index(combo_copy)

        if not positions:
            pos = len(self.actions) + 1
            self.actions[pos] = (self.combo_list[idx],)
        else:
            for pos in positions:
                if pos in self.actions.keys():
                    # add to the end, may support adding to a sequence in future.
                    # should probably throw error if adding to another combo or
                    # sequence as it won't get played
                    # potentially could be a 'back-up' if some rule isn't met.
                    self.actions[pos] = self.actions[pos] + (self.combo_list[idx],)
                else:
                    self.actions[pos] = (self.combo_list[idx],)

        combo_copy.build_word()


    def add_ability(self, ability, positions=None):

        idx = len(self.ability_list)
        self.ability_list.append(ability)

        if not positions:
            pos = len(self.actions) + 1
            self.actions[pos] = (self.ability_list[idx],)
        else:
            for pos in positions:
                if pos in self.actions.keys():
                    # add to the end, may support adding to a sequence in future.
                    # should probably throw error if adding to another combo or
                    # sequence as it won't get played
                    # potentially could be a 'back-up' if some rule isn't met.
                    self.actions[pos] = (self.ability_list[idx],) + self.actions[pos]
                else:
                    self.actions[pos] = (self.ability_list[idx],)


    def get_combo_at(self, position):
        try:
            combo = (i for i in self.actions[position] if isinstance(i, Combo))
            return next(combo)
        except StopIteration as e:
            return None


    def print_rotation(self):
        for i, actions in sorted(self.actions.items()):
            for a in actions:
                print("{0}: {1}".format(i, a.name))


    def print_current_cooldowns(self):
        print("Aiblities Status:")
        [a.status() for a in self.ability_list]
        print("Combo Status:")
        [c.status() for c in self.combo_list]
        #print("Pre-Finisher abilites")
        #[a.status() for a in [al for al  in [c.pre_finishers for c in self.combo_list]]]
        print("Post Abilities:")
        [c.post_ability.status() for c in self.combo_list if c.post_ability is not None]
        print("Pre Finisher Abilities:")
        try:
            [ability.status() for ability in [a for a in [a for a in [c.pre_finishers for c in self.combo_list if c.pre_finishers is not None ]] if len(a) is not 0][0]]
        except IndexError:
            print("No Pre-Finisher abilities")

    def start(self, repeat = False, starttime = None):

        self.print_rotation()

        if self._inprogress:
            pass
        elif starttime is not None:
            self.start_time = starttime
        else:
            # create a timer
            self.start_time = timer()

        self._inprogress = True

        pyautogui.PAUSE = .65

        self.current_action = self.get_combo_at(1)

        for a_idx, items in self.actions.items():

            if self.paused:
                print('paused!')
                self.do_resume()

            # then combos / sequences / spells
            self.current_action = c = self.get_combo_at(a_idx)

            # execute abilities first
            [i.use() for i in items if type(i) is Ability]

            if c is not None:
                if c.cooling_down:
                    # wait for skill to come off CD (but also note the error)
                    print("Skill: %s was used while still on CD" % c.name)
                    print("{:0.2f} seconds left on CD last used at {:0.2f}"\
                    .format(c.cooldown_remaining(), c.cooldown_start))

                c.simluate_keyevents()

        if ( repeat is True or self.repeat is True ) and self.repeat_count > 0:
            self.repeat_count -= 1
            self.start(repeat, timer())
        else:
            self.total_time = timer() - self.start_time
            self.print_current_cooldowns()
            self.end()

            # record combo events
            #[c.record() for c in self.combo_list if type(c) is Combo]


    def end(self):
        print( "Rotation Complete! Total time taken: {:0.2f}".format( self.total_time ))

        # check repeat options, see many time we've run the Rotation
        # use a filler to get a CD or buff back, potentially. Even a single repeat_until
        # rotation of simple combos.
        [i.cooldown.cancel() for i in self.ability_list if i.cooldown is not None]
        [[i.cooldown.cancel() for i in x if i.cooldown is not None] for x in [j.pre_finishers for j in self.combo_list]]
        [i.cooldown.cancel() for i in self.combo_list if i.cooldown is not None]


    def replay(self):
        print( "Replaying events:" )
        #print( [k.time for k in self.current_action.key_events] )
        for c in self.combo_list:
            if c.key_events is not None:
                keyboard.play(c.key_events)
                time.sleep( c.cast_time )
