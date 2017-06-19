import time
import pyautogui
import pywinauto
import datetime
import keyboard
import threading
import queue
import logging
from timeit import default_timer as timer
from sortedcontainers import SortedDict
from pywinauto import application
from copy import copy

# from this application
import generic
from combo import Combo
from ability import Ability

class Rotation(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.exec_lock = threading.Lock()
        self.combo_list = []
        self.ability_list = []
        self.actions = SortedDict()
        self.repeat = False
        self.repeat_count = 0
        self.repeat_until = None
        self.unpause_key = None
        self.paused = False
        self.ending = False
        self.current_action = None
        self.last_keypress = 0.0
        self.last_touched = None

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


    def log_keypress(self, message=None):

        if isinstance(message, Combo):
            msg = "Hotkey for {} was pressed".format(message.name)
        else:
            msg = message

        curr_time = timer()

        delta = curr_time - self.last_keypress

        if self.current_action:
            name = self.current_action.name
        else:
            name = "Unknown"

        logging.debug("During {}, {} ({})".format(
            name, \
            msg, \
            round(timer(), 2)))

        logging.debug("Delta: {}".format(delta))

        self.last_keypress = curr_time


    # This method is designed for fully formed combos that manage their \
    # own hotkey callbacks and doesn't require a copy to be made
    def use(self, action):

        if isinstance(action, Combo):

            if action not in self.combo_list:
                idx = len(self.combo_list)
                self.combo_list.append( action )
                action.register_hotkey( self )
            else:
                idx = self.combo_list.index(action)

            self.last_touched = self.combo_list[idx]

        elif isinstance(action, Ability):
            idx = len(self.ability_list)
            self.ability_list.append(action)
            self.last_touched = self.ability_list[idx]
        else:
            idx = None
            self.last_touched = None
            print("Invalid action passed to Rotation")

        return self


    # This function takes the last touched action and adds it to action_list at
    # the positions determined by *args
    def at(self, *positions):
        # act on the last added combo
        if not positions:
            pos = len(self.actions) + 1
            self.actions[pos] = (self.last_touched,)

        # add to all positions given
        for pos in positions:
            if pos in self.actions.keys():
                # add to the end, may support adding to a sequence in future.
                # should probably throw error if adding to another combo or
                # sequence as it won't get played
                # potentially could be a 'back-up' if some rule isn't met.
                if isinstance(self.last_touched, Combo):
                    self.actions[pos] = self.actions[pos] + (self.last_touched,)
                else:
                    self.actions[pos] = (self.last_touched,) + self.actions[pos]
            else:
                self.actions[pos] = (self.last_touched,)

        return self.last_touched


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


    def run(self):

        pyautogui.PAUSE = .05
        self.print_rotation()

        self.start_time = timer()
        self._inprogress = True

        # create queues for abilities and combos
        ability_q = queue.Queue(5)
        combo_q = queue.Queue(1)

        ## Q consumer function
        def q_worker(type='Ability'):
            which_q = ability_q if type == 'Ability' else combo_q
            while True:
                item = which_q.get()
                if item is None:
                    break

                item.use()
                which_q.task_done()
        ## end consumer

        a_worker = threading.Thread(target=q_worker)
        a_worker.start()

        c_worker = threading.Thread(target=q_worker, args=('Combo',))
        c_worker.start()

        for a_idx, items in self.actions.items():

            self.exec_lock.acquire()

            [ability_q.put(i) for i in items if \
                isinstance(i, Ability) and not \
                isinstance(i, Combo)]

            self.exec_lock.release()

            # current main action
            self.current_action = c = self.get_combo_at(a_idx)
            combo_q.put(c)
            combo_q.join()

        # End the workers
        ability_q.put(None)
        combo_q.put(None)

        if ( self.repeat is True ) and self.repeat_count > 0:
            self.repeat_count -= 1
            self.run()
        else:
            self.total_time = timer() - self.start_time
            self.print_current_cooldowns()
            self.end()


    def end(self):
        print( "Rotation Complete! Total time taken: {:0.2f}".format( self.total_time ))


    def end_destructive(self):
        self.end()

        # check repeat options, see many time we've run the Rotation
        # use a filler to get a CD or buff back, potentially. Even a single repeat_until
        # rotation of simple combos.
        [i.cooldown.cancel() for i in self.ability_list if i.cooldown is not None]
        [[i.cooldown.cancel() for i in x if i.cooldown is not None] for x in [j.pre_finishers for j in self.combo_list]]
        [i.cooldown.cancel() for i in self.combo_list if i.cooldown is not None]

        generic.deregister_keybinds()


    def replay(self):
        print( "Replaying events:" )
        #print( [k.time for k in self.current_action.key_events] )
        for c in self.combo_list:
            if c.key_events is not None:
                keyboard.play(c.key_events)
                time.sleep( c.cast_time )
