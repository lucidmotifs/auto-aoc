import unittest
import logging

import _globals
from combat import Combat, CombatStatus
from rotation import Rotation
from guardian.combos import Counterweight
from guardian.abilities import TacticDefense

logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt='%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)


class CombatTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Combat.stop()

    def test_combat_status_property(self):
        # test initial state
        self.assertEqual(Combat.status, CombatStatus.STOPPED)

        Combat.status = CombatStatus.IN_PROGRESS
        # test state_change event is now set
        self.assertTrue(Combat.state_change.is_set())

    def test_combat_rotation_property(self):
        # test initial
        self.assertEqual(Combat.rotation, None)

        Combat.rotation = Rotation()
        # test _keys private variable for correctness
        self.assertTrue(len(Combat._keys) is 0)

    def test_do_round(self):
        _rot = Rotation()
        _round = (Counterweight(), (TacticDefense(),))
        _rot.add(_round)

        Combat.start_workers()
        Combat.do_round()
        Combat.stop()

        # test output
        keys = [kp.get("key") for kp in _globals.KEY_PRESSES]
        self.assertEqual(''.join(keys), "req")

    def test_do_start(self):
        _rot = Rotation()
        _round = (Counterweight(), (TacticDefense(),))
        _rot.add(_round)

        Combat.do_start()

        self.assertTrue(Combat.workers_exist())
        self.assertEqual(Combat._round, 1)
        self.assertEqual(len(Combat._keys), 1)

    def test_do_restart(self):
        # check log message and Combat status
        # check that finished event has fired
        # check round is 1
        # do equality check on deck
        pass

    def test_do_idle(self):
        """
        Simple check to confirm that Combat idles after rotation is spent.
        Also testing the timeout aspect of the method.
        """
        pass

    def test_do_idle_restart(self):
        """
        Test that restarting rotation works correctly while idling
        """
        pass

    def test_do_idle_terminate(self):
        """
        Test that termination works correctly while idling (no hanging threads)
        """
        pass

    def test_do_terminate(self):
        """
        Test that we can terminate combat at any point with no loose threads
        and that it ends up in a state where combat can be re-initialized
        """
        pass

    def test_run(self):
        """
        Test that running the Combat produces expected key outputs for a
        given rotation
        """
        pass
