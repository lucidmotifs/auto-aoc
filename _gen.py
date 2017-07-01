import pyautogui
import keyboard
import psutil

from timeit import default_timer as timer
from pywinauto import application


KEYBINDS = {
    "LL" : "q",
    "UL" : "1",
    "MID": "2",
    "UR" : "3",
    "LR" : "e",
}
# shorthand
K = KEYBINDS


def register_keybinds(rotation):
    for bind,key in KEYBINDS.items():
        keyboard.add_hotkey(key, rotation.log_keypress, \
            args=["{} attack key was pressed".format(bind)])


def deregister_keybinds():
    for bind,key in KEYBINDS.items():
        keyboard.remove_hotkey(key)


PROCNAME = "AgeOfConanDX10.exe"
#PROCNAME = "notepad.exe"

def _set_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid

    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()
    window.Restore()
    #window.SetFocus()


def _lose_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid
    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()


LAST_KEY_EVENT = 0.0
def dump_key_event(event):
    global LAST_KEY_EVENT
    #print(event.event_type)
    #print(event.name)
    print(event.scan_code)
    if event.event_type is 'down':
        print(round(event.time - LAST_KEY_EVENT, 2))
        LAST_KEY_EVENT = event.timeq


def dump_keys():
    LAST_KEY_EVENT = 0.0
    hk2 = keyboard.hook(dump_key_event)
