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
        pass

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
