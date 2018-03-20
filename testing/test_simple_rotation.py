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
        _rot = Rotation()
        generic.register_keybinds(_rot)

        from rotations import Guardian_DPS
        _rot = Guardian_DPS()

        # Build a test rotation
        Rotation.ability_q = queue.Queue(5)
        Rotation.combo_q = queue.Queue(2)
        # TODO: Rotation.load_actions(_rot)
        Rotation.ability_list = _rot.ability_list
        Rotation.combo_list = _rot.combo_list
        Rotation.actions = _rot.actions

        Rotation.a_worker = threading.Thread( \
                                    target=Rotation.q_worker, \
                                    args=('Ability',))
        # set worker as daemon - still deciding if worked should ALWAYS
        # be a daemon.
        Rotation.a_worker.daemon = True


    def tearDown(self):
        Rotation.end_destructive(Rotation)
        keyboard.unhook_all()


    def test_combo_word(self):
        combo = \
            Rotation.combo_list[random.randrange(0, \
                len(Rotation.combo_list))]
        Rotation.current_action = combo
        combo.rotation = Rotation

        Rotation.c_worker = threading.Thread( \
                                    target=Rotation.q_worker, \
                                    args=('Combo',))
        Rotation.c_worker.daemon = True

        combo.attach_prefinishers( (ActivateChat(),) )

        logging.info("Trying {}".format(combo.name))
        Rotation.combo_q.put(combo)

        Rotation.c_worker.start()
        Rotation.a_worker.start()
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
            Rotation.ability_list[random.randrange(0, \
                len(Rotation.ability_list))]

        Rotation.a_worker = threading.Thread( \
                                    target=Rotation.q_worker, \
                                    args=('Ability',))
        Rotation.a_worker.daemon = True

        Rotation.ability_q.put(ability)
        Rotation.ability_q.put(ActivateChat())
        Rotation.ability_q.put( None )
        Rotation.a_worker.start()
        keys_pressed = input()
        Rotation.a_worker.join()

        # test that the key pressed equals the expected hotkey.
        # test doesn't yet account for modifers - TODO

        self.assertEqual(keys_pressed, ability.hotkey)


if __name__ == '__main__':
    unittest.main()
