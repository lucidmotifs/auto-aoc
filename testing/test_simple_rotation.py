9
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
import _gen
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

class RotationTestCase(unittest.TestCase):

    def setUp(self):
        from rotations import Conqueror_DPS
        self._rotation = Conqueror_DPS()
        _gen.register_keybinds(self._rotation)

        #self._keys_pressed = ""
        #hook = keyboard.hook(self.capture_keyevent)


    def tearDown(self):
        self._rotation.end_destructive()
        Rotation.ability_q = queue.Queue(5)
        Rotation.combo_q = queue.Queue(1)

        keyboard.unhook_all()


    def capture_keyevent(self, event):
        self._keys_pressed += event.name


    def test_rotation_output(self):
        # Create a hook to capture all output
        self._keys_pressed = list()
        hk = keyboard.hook(lambda e: self._keys_pressed.append(e.name))

        self._rotation.use( _enter ).at()
        self._rotation.attack_interval = 0.0
        rotation_thread = threading.Thread( \
                                          target=self._rotation.do_start)

        rotation_thread.start()
        rotation_thread.join()

        self.assertEqual(''.join(self._keys_pressed),
                                 self._rotation.get_word())


    def test_combo_word(self):
        combo = \
            self._rotation.combo_list[random.randrange(0, \
                len(self._rotation.combo_list))]
        self._rotation.current_action = combo
        self._rotation.start_workers()

        combo.rotation = self._rotation

        combo.attach_prefinishers( (_enter,) )

        logging.info("Trying {}".format(combo.name))
        Rotation.combo_q.put(combo)

        self._keys_pressed = input()

        Rotation.combo_q.join()
        Rotation.ability_q.join()

        Rotation.combo_q.put( None )
        Rotation.ability_q.put( None )

        # expected output
        expected = combo.hotkey
        for s in combo.steps:
            expected += s

        self.assertEqual(self._keys_pressed, expected)


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
        self.assertEqual(self._keys_pressed, ability.hotkey)


if __name__ == '__main__':
    unittest.main()
