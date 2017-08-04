import sys, os
import unittest
#print(os.path.abspath('..'))
#sys.path.insert(0, os.path.abspath('..'))


# general utltily
import logging
import random
import time
import unittest
import threading
import queue
import test.support

# keyboard hooks
import keyboard
import pyautogui
import pywinauto

# timing module
from timeit import default_timer as timer

from sortedcontainers import SortedDict

# from this application
#import ipdb; ipdb.set_trace()
sys.path.append(u"C:/Users/paulcooper/Documents/GitHub/auto-aoc")
import _globals
from rotation import Rotation
from ability import Ability
from ability import cooldown_actions
from combo import Combo

# use conqueror for simplicity in testing
from conqueror.abilities import *
from conqueror.combos import *

logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt = '%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)


class ActivateChat(Ability):

    def __init__(self):
        super().__init__("Enter Chat", 0.0)
        self.hotkey = 'enter'

_enter = ActivateChat()

class RotationTestCase(unittest.TestCase):

    def setUp(self):
        self._rotation = Rotation()

        # Combos
        self._rotation.use( Breech(4) ).at( 1 )
        self._rotation.use( Whirlwind() ).at( 2 )
        self._rotation.use( BloodyHack(6) ).at( 3 )
        self._rotation.use( BloodyHack(5) ).at( 4 )

        # Abilities
        #conq_dps.use( BladeWeave() ).at( 1 )
        #conq_dps.use( UseDiscipline() ).at( 2 )
        self._rotation.use( Annihilate() ).at( 3 )
        self._rotation.use( RendFlesh() ).at( 4 )

        _globals.register_keybinds(self._rotation)


    def tearDown(self):
        self._rotation.do_terminate()

        if not self._rotation.terminated.wait(5):
            logging.error("Rotation was never brought down")

        keyboard.unhook_all()


    def capture_keyevent(self, event):
        self._keys_pressed += event.name


    def test_rotation_word_is_string(self):
        self.assertTrue(isinstance(self._rotation.get_word(), str))


    def test_rotation_output(self):
        _globals.attack_int_override = 0.2
        rotation_thread = threading.Thread( \
                                          target=self._rotation.do_start)

        rotation_thread.start()
        rotation_thread.join()

        self.assertEqual(''.join(self._rotation._keys_pressed),
                                 self._rotation.get_word())


    def test_ability_hotkey(self):
        ability = \
            self._rotation.ability_list[random.randrange(0, \
                len(self._rotation.ability_list))]

        logging.info("Testing ability: {}".format(ability.name))

        a_worker = threading.Thread(target=self._rotation.q_worker, \
                                    args=('Ability',))
        a_worker.start()

        Rotation.ability_q.put(ability)
        Rotation.ability_q.put(_enter)

        self._keys_pressed = input()

        Rotation.ability_q.join()

        Rotation.ability_q.put( None )
        a_worker.join()

        # test that the key pressed equals the expected hotkey.
        # test doesn't yet account for modifers - TODO
        self.assertEqual(''.join(self._rotation._keys_pressed),\
                         ability.hotkey)


    def test_rotation_restart(self):
        _globals.attack_int_override = 0.2
        rotation_thread = threading.Thread( \
                                          target=self._rotation.do_start)

        rotation_thread.start()

        while self._rotation._status is not "idle":
            time.sleep(2)

        # rotation is now idling
        self._rotation.do_restart()
        self._rotation.do_terminate()

        """while self._rotation._status is not "idle":
            time.sleep(2)

        self._rotation.do_terminate()"""

        rotation_thread.join()

        self.assertEqual(''.join(self._rotation._keys_pressed),
                                 self._rotation.get_word() * 2)


    def test_rotation_pause_resume(self):
        _globals.attack_int_override = 0.2
        rotation_thread = threading.Thread( \
            target=self._rotation.do_start)

        rotation_thread.start()
        # Now wait for 2 rounds and then pause.
        while True:
            if self._rotation.current_round == 2:
                self._rotation.do_pause('-') # round 2 will complete, paused at 3
                break
            else:
                # keep waiting
                time.sleep(1)

        # If the rotation has paused, the log should read 'pausing...'
        # r.paused should == True, and the current round should still be
        # the same (3) after 3 seconds.
        time.sleep(3)

        self.assertTrue(self._rotation.paused)
        self.assertEqual(self._rotation.current_round, 3)

        found = False
        with open('testing.log', 'r') as logfile:
            for line in logfile:
                if "pausing..." in line.strip():
                    found = True
                    break

        self.assertTrue(found, "'pausing...' not found in log")

        time.sleep(3)

        self._rotation.do_resume()

        time.sleep(3)

        self.assertTrue(not self._rotation.paused)
        self.assertGreater(self._rotation.current_round, 3)

        found = False
        with open('testing.log', 'r') as logfile:
            for line in logfile:
                if "resuming..." in line.strip():
                    found = True
                    break

        self.assertTrue(found, "'resuming...' not found in log")

        # cheap way to end the rotation, should improve.
        self._rotation._terminate = True
        rotation_thread.join()


    def test_empty_items_round_ends(self):
        r = self._rotation

        _globals.attack_int_override = 0.2
        rotation_thread = threading.Thread( \
            target=self._rotation.do_start)

        # Pause the rotation
        r.do_pause()
        self.assertTrue(r.paused)

        rotation_thread.start()
        # Will start but no round will play as rotation is paused.

        if not r.initialized.wait(5):
            self.assertTrue(False, "Rotation never started")

        r.load(dict())

        # ensure items returns None
        self.assertEqual(len(r.on_deck), 0)

        # resume
        r.do_pause()
        self.assertTrue(not r.paused)

        # expected: round exits cleanly and rotation moves to idle.
        if not r.finished.wait(5):
            self.assertTrue(False, "Rotation never ended")

        self.assertEqual(r._status, "idle")

        # Re-load the data and
        r.do_restart()

        self.assertTrue(r.finished.wait(10), "Rotation never finished")



if __name__ == '__main__':
    unittest.main()
