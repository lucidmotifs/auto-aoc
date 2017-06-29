#import sys, os
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

# from this application
import generic
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


class ActivateChat(Ability):

    def __init__(self):
        super().__init__("Enter Chat", 0.0)
        self.hotkey = 'enter'


class RotationTestCase(unittest.TestCase):

    def setUp(self):
        from rotations import Conqueror_DPS
        self._rotation = Conqueror_DPS()
        generic.register_keybinds(self._rotation)

        #self._rotation.start_workers()

        # Build a test rotation
        #self._rotation.ability_q = queue.Queue(5)
        #self._rotation.combo_q = queue.Queue(1)


    def tearDown(self):
        self._rotation.end_destructive()
        keyboard.unhook_all()


    def test_rotation_output(self):
        roation_thread = threading.Thread( \
                                    target=self._rotation.start)
        roation_thread.daemon = True

        roation_thread.start()
        keys_pressed = input()

        self.assertTrue(True)


    def test_combo_word(self):
        combo = \
            self._rotation.combo_list[random.randrange(0, \
                len(self._rotation.combo_list))]
        self._rotation.current_action = combo

        combo.rotation = Rotation

        combo.attach_prefinishers( (ActivateChat(),) )

        logging.info("Trying {}".format(combo.name))
        Rotation.combo_q.put(combo)

        keys_pressed = input()

        Rotation.combo_q.join()
        Rotation.ability_q.join()

        Rotation.combo_q.put( None )
        Rotation.ability_q.put( None )

        # expected output
        expected = combo.hotkey
        for s in combo.steps:
            expected += s

        self.assertEqual(keys_pressed, expected)


    def test_ability_hotkey(self):
        ability = \
            self._rotation.ability_list[random.randrange(0, \
                len(self._rotation.ability_list))]
        logging.info("Testing ability: {}".format(ability.name))

        a_worker = threading.Thread(target=Rotation.q_worker, args=('Ability',))
        a_worker.daemon = True
        a_worker.start()

        Rotation.ability_q.put(ability)
        Rotation.ability_q.put(ActivateChat())

        keys_pressed = input()

        #print("join ability q (size is {})".format(Rotation.qsize()))
        #Rotation.ability_q.join()

        print("ending worker")
        Rotation.ability_q.put( None )

        # test that the key pressed equals the expected hotkey.
        # test doesn't yet account for modifers - TODO
        self.assertEqual(keys_pressed, ability.hotkey)


if __name__ == '__main__':
    unittest.main()
