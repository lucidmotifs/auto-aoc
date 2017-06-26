# general utltily
import logging
import random
import generic
import time
import unittest
import threading

# keyboard hooks
import keyboard
import pyautogui
import pywinauto

# timing module
from timeit import default_timer as timer

# from this application
from rotation import Rotation
from ability import Ability
from ability import COOLDOWN_ACTIONS
from combo import Combo

logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt = '%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)


class RotationTestCase(unittest.TestCase):

    def setUp(self):
        from rotations import Guardian_DPS as gdps
        self.rotation = Rotation()

        #generic.register_keybinds(self.rotation)
        self.rotation = gdps()


    def tearDown(self):
        self.rotation.end_destructive()
        self.rotation = None


    def test_round_combos(self):
        logging.debug("test1")


    def test_round_abilities(self):
        ability = \
            self.rotation.ability_list[random.randrange(0, \
                len(self.rotation.ability_list))]

        self.rotation.ability_q.put(ability)
        self.rotation.ability_q.put( None )

        a_worker = threading.Thread(target=Rotation.q_worker, \
                                    args=(self.rotation, 'Ability',))
        a_worker.start()
        a_worker.join()

        #self.rotation.ability_q.join()
        self.assertEqual(ability.name, ability.name)


if __name__ == '__main__':
    unittest.main()
