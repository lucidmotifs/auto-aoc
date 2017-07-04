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

# from this application
#import ipdb; ipdb.set_trace()
sys.path.append(u"C:/Users/paulcooper/Documents/GitHub/auto-aoc")
import _globals
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

_enter = ActivateChat()

class ComboTestCase(unittest.TestCase):

    def setUp(self):
        self._rotation = Rotation()
        _globals.register_keybinds(self._rotation)


    def tearDown(self):
        self._rotation.end_destructive()
        Rotation.ability_q = queue.Queue(5)
        Rotation.combo_q = queue.Queue(1)

        keyboard.unhook_all()


    def test_combo_word(self):
        # BloodyHack6
        from conqueror.combos import BloodyHack
        combo = BloodyHack(6)

        self._rotation.use( combo ).at()
        self._rotation.start_workers()
        self._rotation.attack_interval = 0.2

        rotation_thread = threading.Thread( \
                                          target=self._rotation.do_start)

        rotation_thread.start()
        rotation_thread.join()

        self.assertEqual(''.join(self._rotation._keys_pressed),
                         ''.join(combo.word))


    def test_combo_ouput(self):
        combo = \
            self._rotation.combo_list[random.randrange(0, \
                len(self._rotation.combo_list))]

        self._rotation.current_action = combo
        self._rotation.start_workers()

        combo.rotation = self._rotation

        combo.attach_prefinisher( _enter )

        logging.info("Trying {}".format(combo.name))
        Rotation.combo_q.put(combo)

        self._keys_pressed = input()

        Rotation.combo_q.put( None )
        Rotation.ability_q.put( None )

        # expected output
        expected = combo.hotkey
        for s in combo.steps:
            expected += s

        self.assertEqual(self._keys_pressed, expected)
