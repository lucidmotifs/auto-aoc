import pyautogui
import threading
import queue
import logging
from timeit import default_timer as timer
from sortedcontainers import SortedDict

# from this application
import _globals
from combo import Combo
from ability import Ability
from world import World
from rotation import Rotation


class CombatStatus():

    IN_PROGRESS = 1
    IDLE = 2
    TERMINATING = 3
    STARTING = 4
    PAUSED = 5
    RESUMING = 6
    STOPPED = 7
    RESTARTING = 8

    UNKNOWN = 0


class CombatMeta(type):
    """ Define properties for the Combat class. """
    @property
    def status(self):
        return getattr(self, '_status', CombatStatus.UNKNOWN)

    @status.setter
    def status(self, value):
        self._status = value
        self.state_change.set()
        logging.info("Combat state set to {}".format(value))

    @property
    def rotation(self):
        return getattr(self, '_rotation', None)

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.load(self._rotation.deck)


class Combat(object, metaclass = CombatMeta):
    """
    The central singleton that passes game objects to the worker queues
    that process the needed inputs. Controls the flow of execution.
    """

    # properties
    _start_time = 0.0
    _end_time = 0.0
    _round = 1
    _inprogress = False
    _status = CombatStatus.STOPPED
    _rotation = None
    _keys = []
    _current_action = None

    # create queues for abilities, spells and combos
    ability_q = queue.Queue(5)
    combo_q = queue.Queue(1)
    spell_q = queue.Queue(1)
    _workers = []

    # the thread that combat flow runs in
    thread = threading.Thread()

    # locks
    exec_lock = threading.Lock()
    pause_lock = threading.Lock()

    # major states
    initialized = threading.Event()
    finished = threading.Event()
    stopped = threading.Event()
    # check status after event
    state_change = threading.Event()

    @classmethod
    def load(cls, deck):
        """
        Loads and intializes a rotation's deque, collects keys to iterate
        through.
        """
        cls.on_deck = deck

        # set keys of actions to execute
        # cls._keys = filter(lambda k: k >= cls._round,
        #                   sorted(cls.on_deck.keys()))
        cls._keys = list(range(len(deck)))[:cls._round]

        cls.finished.clear()

    @classmethod
    def do_round(cls, rnd=0):
        """ Performs a combat round at currenr cursor"""
        # Wait on the round while
        if cls.status is CombatStatus.PAUSED:
            logging.debug("Round stalled due to pause_lock")
            cls.pause_lock.acquire()
            cls.pause_lock.release()

        if rnd is 0:
            rnd = cls._round

        # ensure worker qs are started
        if not cls.workers_exist():
            raise RuntimeError('Cannot do round without workers')

        try:
            logging.info("Round: {}".format(rnd))

            # Retrieve the items for this round
            # looks like (ComboName, (Ability1, Ability2, ...))
            try:
                action = cls.on_deck.popleft()
            except Exception:
                pass

            # Exit round is w ehave no items
            if action is None or len(action) is 0:
                return

            # current main action
            if isinstance(action[0], Combo):
                World._current_action = c = action[0]
            else:
                logging.error("Got bad type for action %s" % type(action[0]))
                c = None

            def is_ability(a):
                return isinstance(a, Ability) and not isinstance(a, Combo)

            # put abilities into the ability queue.
            _abilities = list(filter(is_ability, action[1]))

            for a in _abilities:
                a.combat = cls
                Combat.ability_q.put(a, timeout=5)

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
                Combat.combo_q.put(c, timeout=5)

                # Ensure pre-finisher abilities fire.
                if c.pre_finishers:
                    # print("Joining Ability Q")
                    Combat.ability_q.join()

                # Wait for combo to end.
                # print("Joining Combo Q")
                Combat.combo_q.join()
        except queue.Full as e:
            logging.debug("A Queue is Full")
            logging.error(e)
        except Exception as e:
            logging.exception('Got exception during round')

    @classmethod
    def do_start(cls):
        cls.start_time = timer()
        cls.print_rotation()
        cls.start_workers()
        cls.do_restart()

        # Signal that the rotation has started
        cls.initialized.set()

        cls.run()

    @classmethod
    def do_restart(cls):
        if cls._inprogress:
            logging.info("Restarting")
            cls.status = CombatStatus.RESTARTING

        # if the rotation has finished, set the restarted event
        if cls.finished.is_set():
            cls.finished.clear()

        # Reset the round number
        cls._round = 1

        # Load a copy of the actions queue
        cls.load(cls.rotation.deck())

    @classmethod
    def do_idle(cls, secs):
        """
        Idles until a timeout or status change. Returns True if progress
        should continue, and False if the rotation should end.
        """

        if cls._status is not CombatStatus.TERMINATING:
            cls._status = CombatStatus.IDLE
            logging.info("waiting for {} secs...".format(secs))

        # Set the rotation to finished
        cls.finished.set()

        # Wait for either a state change or timeout
        if cls.state_change.wait(secs):
            if cls.status is CombatStatus.TERMINATING:
                return False
            elif cls.status is CombatStatus.RESTARTING:
                return True
            else:
                logging.info("Status is {}".format(cls.status))

            # Acted upon new state, clearing event.
            cls.state_change.clear()
        else:
            # timedout
            return False

    @classmethod
    def do_terminate(cls):
        if cls._inprogress:
            # will terminate at the end of the rotation
            # to improve this to terminate immediately, we need to clear
            # the _keys property as well.
            logging.info("Terminating.")

        cls.status = CombatStatus.TERMINATING

        # End the run loop
        cls._inprogress = False

    @classmethod
    def run(cls):
        pyautogui.PAUSE = .05

        cls._inprogress = True

        # Setting and clearing state change event
        cls.status = CombatStatus.IN_PROGRESS
        cls.state_change.clear()

        # main loop
        while cls._inprogress:
            try:
                cls.current_round = next(cls._keys)
                cls.do_round()
            except StopIteration:
                if cls._inprogress:
                    cls._inprogress = cls.do_idle(60)
                else:
                    break
        if cls.status is CombatStatus.TERMINATING:
            cls.end_destructive()
        else:
            logging.debug("Ending loop, _inprogress is False")
            cls.stop()

    def workers_exist():
        if len(Combat._workers) is 0:
            return False
        else:
            return True

    @staticmethod
    def create_workers():
        workers = []

        a_worker = threading.Thread(
            target=Combat.q_worker, args=('Ability',))
        a_worker.start()

        c_worker = threading.Thread(target=Combat.q_worker, args=('Combo',))
        c_worker.start()

        workers.append(a_worker)
        workers.append(c_worker)

        return workers

    @staticmethod
    def start_workers():
        """Start the workers"""
        if not Combat.workers_exist():
            Combat._workers = Combat.create_workers()

    @staticmethod
    def end_workers():
        """End the workers"""

        logging.debug("Ending workers - potential block")

        if Combat.combo_q:
            Combat.combo_q.put(None)
            Combat.combo_q.join()

        if Combat.ability_q:
            Combat.ability_q.put(None)
            Combat.ability_q.join()

        logging.debug("Workers ended - block potential finished")

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
                    logging.debug(
                        "None passed to {} worked, ending.".format(T))
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

    @classmethod
    def stop(cls):
        try:
            cls.pause_lock.release()
            cls.exec_lock.release()
        except Exception:
            pass

        cls.end_workers()

        cls._total_time = timer() - cls._start_time
        World.print_current_cooldowns()

        logging.debug("Combat Over! Total time: {:0.2f}"
                      .format(cls._total_time))

        cls.stopped.set()

    # TODO - move to specific cooldown handling class
    # as deconstructor
    def end_destructive(self):
        if not self.stopped.is_set():
            self.stop()
