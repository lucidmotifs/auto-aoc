import unittest

# general utility
import logging
import time
import threading
import queue

# keyboard hook
import keyboard
import _globals
from rotation import Rotation
from ability import Ability

logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt='%M:%S',
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
        from conqueror.combos import BloodyHack
        combo = BloodyHack(6)

        self._rotation.use(combo).at()
        self._rotation.start_workers()
        _globals.attack_int_override = 0.2

        rotation_thread = threading.Thread(target=self._rotation.do_start)

        rotation_thread.start()

        # wait for combo time
        time.sleep(1)
        self._rotation.do_terminate()
        rotation_thread.join()

        self.assertEqual(''.join(self._rotation._keys_pressed),
                         ''.join(combo.word))

    def test_combo_ouput(self):
        from conqueror.combos import Whirlwind
        combo = Whirlwind()

        self._rotation.use(combo).at()
        self._rotation.start_workers()
        _globals.attack_int_override = 0.2

        rotation_thread = threading.Thread(target=self._rotation.do_start)

        rotation_thread.start()
        # wait for combo time
        time.sleep(1)
        self._rotation.do_terminate()
        rotation_thread.join()

        # expected output
        expected = combo.hotkey
        for s in combo.steps:
            expected += s

        self.assertEqual(''.join(self._rotation._keys_pressed), expected)

    def test_combo_cooldown_skip(self):
        from guardian.combos import TitanicSmash
        combo = TitanicSmash()

        self._rotation.use(combo).at(1, 2)
        self._rotation.start_workers()

        _globals.attack_int_override = 0.2

        rotation_thread = threading.Thread(target=self._rotation.do_start)

        with self.assertLogs(level='INFO') as cm:
            rotation_thread.start()

            while self._rotation._status is not "idle":
                time.sleep(2)

            # End rotation
            self._rotation.do_terminate()
            rotation_thread.join()

        self.assertEqual(''.join(self._rotation._keys_pressed),
                         combo.word)

        self.assertTrue(
            'Skipping execution of {} due to cooldown'.format(combo.name),
            cm.output)

    def test_combo_cooldown_wait(self):
        pass
