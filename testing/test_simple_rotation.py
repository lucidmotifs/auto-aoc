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

class RotationTestCase(unittest.TestCase):

    def setUp(self):
        from rotations import Conqueror_DPS
        self._rotation = Conqueror_DPS()
        _globals.register_keybinds(self._rotation)

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
        self._rotation.use( _enter ).at()
        self._rotation.attack_interval = 0.2
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
        self.assertEqual(self._keys_pressed, ability.hotkey)


if __name__ == '__main__':
    unittest.main()
