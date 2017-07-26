import time
import pyautogui
import pywinauto
import datetime
import keyboard
import threading
import queue
import logging
import datetime
from timeit import default_timer as timer
from sortedcontainers import SortedDict
from pywinauto import application
from copy import copy

# from this application
import _globals
from combo import Combo
from ability import Ability

class Rotation(threading.Thread):

    combo_list = []
    ability_list = []
    start_time = timer()
    last_keypress = 0.0
    exec_lock = threading.Lock()
    pause_lock = threading.Lock()

    # create queues for abilities and combos  (spells tbd)
    ability_q = queue.Queue(5)
    combo_q = queue.Queue(1)

    def __init__(self):
        threading.Thread.__init__(self)

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
        self.last_touched = None
        self._keys_pressed = []

        # timers
        self.start_time = 0.0
        self.end_time = 0.0

        self._status = "stopped"
        self._inprogress = False
        # used to exit currently running queue - remove after deque branch
        # is merged
        self._terminate = False

        # progress
        self.current_round = 1
        self.on_deck = dict()


    def do_resume(self):
        if self.unpause_key is not None:
            keyboard.remove_hotkey(self.unpause_key)

            # change activation
            keyboard.add_hotkey(self.unpause_key, self.do_pause, \
                                args=[self.unpause_key])


        self.paused = False

        # release lock
        self.pause_lock.release()


    def do_pause(self, key_pressed):
        # pause the rotation in place, but allow CDs to finish (CDs in threads)
        # i.e. we are not pausing the thread / process
        if self.paused:
            logging.debug("resuming...")
            self.paused = False
            self.pause_lock.release()
        else:
            logging.debug("pausing...")
            self.paused = True
            self.pause_lock.acquire()


    def log_keypress(self, message, key):
        self._keys_pressed.append(key)
        if isinstance(message, Ability):
            msg = "Hotkey for {} was pressed".format(message.name)
        else:
            msg = message

        curr_time = timer()

        delta = curr_time - self.last_keypress
        self.last_keypress = curr_time

        if self.current_action:
            name = self.current_action.name
        else:
            name = "Unknown"

        logging.debug("During {}, {} ({})".format(
            name, \
            msg, \
            round(timer(), 2)))

        logging.debug("Delta: {}".format(delta))


    # This method is designed for fully formed combos that manage their \
    # own hotkey callbacks and doesn't require a copy to be made
    def use(self, action):

        if isinstance(action, Combo):

            if action not in self.combo_list:
                idx = len(self.combo_list)
                self.combo_list.append( action )
            else:
                idx = self.combo_list.index(action)

            self.last_touched = self.combo_list[idx]

            # Set the rotation property for all action types.
            action.rotation = self

        elif isinstance(action, Ability):

            idx = len(self.ability_list)

            self.ability_list.append(action)
            self.last_touched = self.ability_list[idx]

            # Set the rotation property for all action types.
            action.rotation = self

        elif action is None:

            self.last_touched = action

        else:

            idx = None
            self.last_touched = None
            logging.info("Invalid action passed to Rotation")

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
                if isinstance(self.last_touched, Combo): # TODO add Spell
                    self.actions[pos] = self.actions[pos] + (self.last_touched,)
                else: # is Ability so add to end
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


    def get_word(self):
        word = list()
        for i, actions in sorted(self.actions.items()):
            for a in actions:
                word.append(a.word)

        return ''.join(word)


    def print_rotation(self):
        for i, actions in sorted(self.actions.items()):
            for a in actions:
                logging.debug("{0}: {1}".format(i, a.name))


    def print_current_cooldowns(self):
        logging.debug("Abilities Status:")
        [a.status() for a in self.ability_list]
        logging.debug("Combo Status:")
        [c.status() for c in self.combo_list]

        try:
            logging.debug("Post Abilities:")
            [ability.status() for ability in [a for a in [a for a in \
            [c.post_finishers for c in self.combo_list if c.post_finishers is not None ]] if len(a) is not 0][0]]
        except IndexError:
            logging.debug("No Post-Finisher abilities")

        try:
            logging.debug("Pre Finisher Abilities:")
            [ability.status() for ability in [a for a in [a for a in \
            [c.pre_finishers for c in self.combo_list if c.pre_finishers is not None ]] if len(a) is not 0][0]]
        except IndexError:
            logging.debug("No Pre-Finisher abilities")


    def do_round(self, rnd=0):
        """ Perform the action at position specified by rnd """
        # Wait on the round while
        if self.paused:
            self.pause_lock.acquire()
            self.pause_lock.release()

        if rnd is 0:
            rnd = self.current_round

        try:
            logging.info("Round: {}".format(rnd))
            items = self.on_deck.pop(rnd, None)

            # put abilities into the ability queue.
            def is_ability(a):
                return isinstance(a, Ability) and not isinstance(a, Combo)

            _abilities = list(filter(is_ability, items))

            for a in _abilities:
                Rotation.ability_q.put(a)

            # Ensure abilities fire first.
            if _abilities:
                Rotation.ability_q.join()

            # current main action, exec lock should be set within
            # and abilities won't be able to fire.
            self.current_action = c = self.get_combo_at(rnd)
            if c:
                #print("Interval {}".format(interval))
                c.attack_interval = \
                    _globals.attack_int_override or c.attack_interval
                #print("Attack Interval {}".format(c.attack_interval))
                #print("Putting {} into queue".format(c.name))
                Rotation.combo_q.put(c)

                # Ensure pre-finisher abilities fire.
                if c.pre_finishers:
                    #print("Joining Ability Q")
                    Rotation.ability_q.join()

                # Wait for combo to end.
                #print("Joining Combo Q")
                Rotation.combo_q.join()
        except queue.Full as e:
            logging.debug("A Queue is Full")
            logging.error(e)


    def create_workers(self):
        workers = []

        a_worker = threading.Thread(target=Rotation.q_worker, args=('Ability',))
        a_worker.start()

        c_worker = threading.Thread(target=Rotation.q_worker, args=('Combo',))
        c_worker.start()

        workers.append(a_worker)
        workers.append(c_worker)

        return workers


    def start_workers(self):
        """Start the workers"""
        if not hasattr(self, '_workers'):
            self._workers = self.create_workers()


    def end_workers(self):
        """End the workers"""
        logging.debug("Ending workers - potential block")
        Rotation.combo_q.put( None )
        Rotation.combo_q.join()

        Rotation.ability_q.put( None )
        Rotation.ability_q.join()


    def load(self, A):
        # TODO register hotkeys, add to ability/combo/spell list
        # ...
        self.on_deck = A


    def do_start(self):
        self.start_time = timer()
        self.print_rotation()
        self.start_workers()
        self.do_restart()
        self.run()


    def do_restart(self):
        if self._inprogress:
            print("Restarting...")
            self._status = "restarting"

        self.current_round = 1
        # Reset the Qs
        # Rotation.ability_q = queue.Queue(5)
        # Rotation.combo_q = queue.Queue(1)

        # Create a copy of the actions queue
        self.load(self.actions.copy())

        # set keys of actions to execute
        self._keys = filter( lambda k: k >= self.current_round, \
                     sorted(self.on_deck.keys()))



    def do_idle(self, mins):
        """ Idles until a timeout of status change. Returns True if progress
        should continue, and False if the rotation should end. """
        self._status = "idle"
        # the rotation has ended
        # self._inprogress = False

        logging.info("idling...")

        # the time we'll wait in idle before exiting the program
        timeout = datetime.datetime.now() + datetime.timedelta(minutes = mins)

        while datetime.datetime.now() < timeout and self._status == "idle":
            time.sleep(1)

        if self._status == "idle" or self._status == "terminating":
            # timeout or terminated
            return False
        elif self._status == "restarting":
            return True


    def do_terminate(self):
        if self._inprogress:
            # will terminate at the end of the rotation
            # to improve this to terminate immediately, we need to clear
            # the _keys property as well.
            self._terminate = True

            print("Terminating...")
            self._status = "terminating"

        else:
            self._status = "terminating"


    def run(self):
        pyautogui.PAUSE = .05

        self._inprogress = True
        self._status = "running"

        # main loop
        while True:
            # exit loop if porogress is stopped
            if not self._inprogress:
                break
            try:
                self.current_round = next(self._keys)
                self.do_round()
            except StopIteration:
                if self._inprogress and not self._terminate:
                    self._inprogress = self.do_idle(5)
                else:
                    break

        if self._terminate:
            self.end_destructive()
        else:
            self.end()


    @classmethod
    def q_worker(cls, T='Ability'):
        """Q consumer function"""
        # TODO: set the argument to a python Type rather than a string
        which_q = cls.ability_q if T == 'Ability' else cls.combo_q
        logging.info("Creating {} worker".format(T))

        while True:
            try:
                #print("Attempting to get item from {} queue".format(T))
                item = which_q.get()

                if item is None:
                    which_q.task_done()
                    logging.debug("None passed to {} worked, ending.".format(T))
                    break

                #print("Found {} in {}, processing.".format(item.name, T))
                """print( \
                    "There are {} items in {} Q" \
                    .format(Rotation.combo_q.qsize(), T))"""
            except queue.Empty as e:
                logging.error("{} empty for too long".format(T))
                break
            except Exception as e:
                logging.error("Exception in {} queue: {}".format(T, e))

            item.use(cls)
            which_q.task_done()
        ## end consumer


    def end(self):
        self.end_workers()

        self.total_time = timer() - self.start_time
        self.print_current_cooldowns()

        logging.debug( "Rotation Complete! Total time taken: {:0.2f}"\
                       .format( self.total_time ))

        self._inprogress = False


    def end_destructive(self):
        if self._inprogress:
            self.end()

        self._key_pressed = list()

        # check repeat options, see many time we've run the Rotation
        # use a filler to get a CD or buff back, potentially. Even a single repeat_until
        # rotation of simple combos.
        [i.cooldown.cancel() for i in self.ability_list if i.cooldown is not None]
        [[i.cooldown.cancel() for i in x if i.cooldown is not None] for x in [j.pre_finishers for j in self.combo_list]]
        [i.cooldown.cancel() for i in self.combo_list if i.cooldown is not None]


    # Not functional at the moment
    def replay(self):
        logging.debug( "Replaying events:" )
        #logging.debug( [k.time for k in self.current_action.key_events] )
        for c in self.combo_list:
            if c.key_events is not None:
                keyboard.play(c.key_events)
                time.sleep( c.cast_time )
