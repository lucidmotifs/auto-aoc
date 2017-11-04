import keyboard
import logging
import psutil

from timeit import default_timer as timer
from pywinauto import application


KEYBINDS = {
    "LL": "q",
    "UL": "1",
    "MID": "2",
    "UR": "3",
    "LR": "e",
}
# shorthand
K = KEYBINDS

# Process name to switch to
PROCNAME = "AgeOfConanDX10.exe"

# Attack intervals for various weapons
attack_int_override = None
attack_int_1he = .75

# Time to wait after hotkey for first step
opener_wait = .3

# Debugging = True will print thigs to the console
DEBUG = False

LAST_KEY_PRESS = {
    "key": None,
    "timestamp": 0,
    "delta": 0
}

KEY_PRESSES = []

LAST_KEY_EVENT = 0.0


def register_keybinds():
    """
    Register basic/global keybindings
    """
    for bind, key in KEYBINDS.items():
        keyboard.add_hotkey(
            key, log_keypress,
            args=["{} attack key was pressed".format(bind), key])


def deregister_keybinds():
    for bind, key in KEYBINDS.items():
        keyboard.remove_hotkey(key)


def _set_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid

    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()
    window.Restore()
    # window.SetFocus()


def _lose_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid
    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()


def dump_key_event(event):
    global LAST_KEY_EVENT
    # print(event.event_type)
    # print(event.name)
    print(event.scan_code)
    if event.event_type is 'down':
        print(round(event.time - LAST_KEY_EVENT, 2))
        LAST_KEY_EVENT = event.timeq


def dump_keys():
    global LAST_KEY_EVENT
    LAST_KEY_EVENT = 0.0
    hk2 = keyboard.hook(dump_key_event)

    return hk2


def log_keypress(key, message, during=None):

    now = timer()
    last = LAST_KEY_PRESS["timestamp"]
    LAST_KEY_PRESS["key"] = key
    LAST_KEY_PRESS["delta"] = now - last
    LAST_KEY_PRESS["timestamp"] = now

    KEY_PRESSES.append(LAST_KEY_PRESS.copy())

    name = during.name if during is not None else "Unknown"

    logging.debug("During {}, {} ({})".format(
        name,
        message,
        round(now, 2)))

    logging.debug("Delta: {}".format(LAST_KEY_PRESS["delta"]))
