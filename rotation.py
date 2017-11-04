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

    # locks
    exec_lock = threading.Lock()
    pause_lock = threading.Lock()

    # events
    # major states
    initialized = threading.Event()
    finished = threading.Event()
    stopped = threading.Event()
    # minor states, check status after event
    state_change = threading.Event()

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


    def status():
        doc = "The status property."
        def fget(self):
            return self._status
        def fset(self, value):
            self._status = value
            self.state_change.set()
            logging.info("Rotation state set to {}".format(value))
        def fdel(self):
            del self._status
        return locals()
    status = property(**status())

    def do_pause(self):
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


    def use(self, action):
        """
        This method is designed for fully formed combos that manage their
        own hotkey callbacks and doesn't require a copy to be made.
        """

        if isinstance(action, Combo):

            if action not in self.combo_list:
                idx = len(self.combo_list)
                #schedule = action.schedule
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

    def at(self, *positions):
        """
        This function takes the last touched action and adds it to action_list
        at the positions determined by *args
        """
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
            logging.debug("Round stalled due to pause_lock")
            self.pause_lock.acquire()
            self.pause_lock.release()

        if rnd is 0:
            rnd = self.current_round

        try:
            logging.info("Round: {}".format(rnd))

            # Retrieve the items for this round
            items = self.on_deck.pop(rnd, None)

            # Exit round is w ehave no items
            if not items:
                return

            # current main action
            self.current_action = c = self.get_combo_at(rnd)

            def is_ability(a):
                return isinstance(a, Ability) and not isinstance(a, Combo)

            # put abilities into the ability queue.
            _abilities = list(filter(is_ability, items))

            for a in _abilities:
                Rotation.ability_q.put(a)

            # Ensure abilities fire first.
            # if _abilities or not Rotation.ability_q.empty():
            #    print("Firing abilities")
            #    Rotation.ability_q.join()

            # run the combo
            if c:
                # print("Interval {}".format(interval))
                c.attack_interval = \
                    _globals.attack_int_override or c.attack_interval
                # print("Attack Interval {}".format(c.attack_interval))
                # print("Putting {} into queue".format(c.name))
                Rotation.combo_q.put(c)

                # Ensure pre-finisher abilities fire.
                if c.pre_finishers:
                    # print("Joining Ability Q")
                    Rotation.ability_q.join()

                # Wait for combo to end.
                # print("Joining Combo Q")
                Rotation.combo_q.join()
        except queue.Full as e:
            logging.debug("A Queue is Full")
            logging.error(e)
        except Exception as e:
            logging.exception('Got exception during round')

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

        if Rotation.combo_q:
            Rotation.combo_q.put( None )
            Rotation.combo_q.join()

        if Rotation.ability_q:
            Rotation.ability_q.put( None )
            Rotation.ability_q.join()

        logging.debug("Workers ended - block potential finished")

    def load(self, A):
        # TODO register hotkeys, add to ability/combo/spell list
        # ...
        self.on_deck = A

        # set keys of actions to execute
        self._keys = filter(lambda k: k >= self.current_round,
                            sorted(self.on_deck.keys()))

        self.finished.clear()

    def do_start(self):
        self.start_time = timer()
        self.print_rotation()
        self.start_workers()
        self.do_restart()

        # Signal that the rotation has started
        self.initialized.set()

        self.run()

    def do_restart(self):
        if self._inprogress:
            logging.info("Restarting")
            self.status = "restarting"

        # if the rotation has finished, set the restarted event
        if self.finished.is_set():
            self.finished.clear()

        # Reset the round number
        self.current_round = 1

        # Load a copy of the actions queue
        self.load(self.actions.copy())

    def do_idle(self, secs):
        """
        Idles until a timeout or status change. Returns True if progress
        should continue, and False if the rotation should end.
        """

        if self._status is not "terminating":
            self._status = "idle"
            logging.info("waiting for {} secs...".format(secs))

        # Set the rotation to finished
        self.finished.set()

        # Wait for either a state change or timeout
        if self.state_change.wait(secs):
            if self.status is "terminating":
                return False
            elif self.status is "restarting":
                return True
            else:
                logging.info("Status is {}".format(self.status))

            # Acted upon new state, clearing event.
            self.state_change.clear()
        else:
            # timeout
            return False

    def do_terminate(self):
        if self._inprogress:
            # will terminate at the end of the rotation
            # to improve this to terminate immediately, we need to clear
            # the _keys property as well.
            logging.info("Terminating.")

        self.status = "terminating"

        # End the run loop
        self._inprogress = False

    def run(self):
        pyautogui.PAUSE = .05

        self._inprogress = True

        # Setting and clearing state change event
        self.status = "running"
        self.state_change.clear()

        # main loop
        while self._inprogress:
            try:
                self.current_round = next(self._keys)
                self.do_round()
            except StopIteration:
                if self._inprogress:
                    self._inprogress = self.do_idle(60)
                else:
                    break
        if self.status is "terminating":
            self.end_destructive()
        else:
            logging.debug("Ending loop, _inprogress is False")
            self.stop()

    @classmethod
    def q_worker(cls, T='Ability'):
        """Q consumer function"""
        # TODO: set the argument to a python Type rather than a string
        which_q = cls.ability_q if T == 'Ability' else cls.combo_q
        logging.info("Creating {} worker".format(T))

        while True:
            try:
                # print("Attempting to get item from {} queue".format(T))
                item = which_q.get()

                if item is None:
                    which_q.task_done()
                    logging.debug("None passed to {} worked, ending.".format(T))
                    break

                # print("Found {} in {}, processing.".format(item.name, T))
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
        # end consumer
        which_q = None

    def stop(self):
        try:
            self.pause_lock.release()
            self.exec_lock.release()
        except Exception:
            pass

        self.end_workers()

        self.total_time = timer() - self.start_time
        self.print_current_cooldowns()

        logging.debug("Rotation Complete! Total time taken: {:0.2f}"
                      .format(self.total_time))

        self.stopped.set()

    # TODO make this a deconstructor that removes blocks and
    # ends cooldowns + threads (and checks if any threads left alive)
    # then create a 'stop' method to replace anything left over.
    def end_destructive(self):
        if not self.stopped.is_set():
            self.stop()

        self._key_pressed = list()

        # check repeat options, see many time we've run the Rotation
        # use a filler to get a CD or buff back, potentially. Even a single
        # repeat_until rotation of simple combos.
        [i.cooldown.cancel() for i in self.ability_list if i.cooldown is not None]
        [[i.cooldown.cancel() for i in x if i.cooldown is not None] for x in [j.pre_finishers for j in self.combo_list]]
        [i.cooldown.cancel() for i in self.combo_list if i.cooldown is not None]

    def replay(self):
        """
        Not functional at the moment
        """
        logging.debug("Replaying events:")
        # logging.debug( [k.time for k in self.current_action.key_events] )
        for c in self.combo_list:
            if c.key_events is not None:
                keyboard.play(c.key_events)
                time.sleep(c.cast_time)
