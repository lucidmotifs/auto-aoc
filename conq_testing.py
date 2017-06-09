import time
import pyautogui
import pywinauto
import datetime
import keyboard
import threading
import logging
import psutil
from timeit import default_timer as timer
from pywinauto import application
from copy import copy

# from this application
from ability import Ability
from ability import COOLDOWN_ACTIONS
from combo import Combo
from rotation import Rotation

# TESTING / DEBUG / PROD
RUN_LEVEL = "TESTING"

KEYBINDS = {
    "LL" : "q",
    "UL" : "1",
    "MID": "2",
    "UR" : "3",
    "LR" : "e",
}
# shorthand
K = KEYBINDS

AOC_EXE_LOCATION = u"C:\Program Files (x86)\Steam\SteamApps\common\Age of Conan\AgeOfConanDX10.exe"
NOTEPAD = u'C:\\WINDOWS\\system32\\notepad.exe'

PROCNAME = "AgeOfConanDX10.exe"

logging.basicConfig(format='%(message)s', filename='output.txt', filemode='w', level=logging.DEBUG)

def AOC_set_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid

    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()
    window.Restore()

    time.sleep(.5) # allow time for window switching


def AOC_lose_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid
    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()


def DEBUG_set_focus():
    app = application.Application()
    app = app.start("Notepad.exe")
    window = app.top_window_()
    window.Minimize()
    window.Restore()
    window.set_focus()

    time.sleep(.5)


class conq_breech(Combo):

    def __init__(self, rank="III"):
        super().__init__("Breech", "4", self.set_steps(rank), 43, 1.5, post_ability=None)
        self.step_delays = {}


    def set_steps(self, rank):
        self.steps = ["1"]
        self.execute_time = 1.0

        return self.steps

if RUN_LEVEL == "TESTING":
    AOC_set_focus()
elif RUN_LEVEL == "PROD":
    # assume we're running from in-game
    time.sleep(100)


breech = conq_breech()

whirlwind = Combo("Whirlwind", ('r',), ["e","q",], "3", 10, 1.5)

bloodbath = Combo("Bloodbath V", ('t',), ["q","e",], "2", 10, 2.0)
bloodbath.should_weave = False

bloodyhack = Combo("Bloody Hack VI", ('f',), ["2", "q",], "3", 1, 1.5)
bloodyhack.should_weave = True

bloodyhackV = Combo("Bloody Hack V", ('shift', 'r',), ["2",], "3", 1, 1)
bloodyhackV.should_weave = True

# Add a 300ms to the first step
# bloodyhackV.add_delay(1, .1)
# whirlwind.add_delay(1, .2)

annihilate = Ability("Annihilate", ('5',), 180, 0, 20)
rend_flesh = Ability("Rend Flesh", ('g',), 60, 0, 20)

# Abilities
bloodyvengance = Ability("Bloody Vengance", ('5',), 27, 1.5, 0)
reckoning = Ability("Reckoning", ('q',), 10, 0, 0)
powerhouse = Ability("Powerhouse", ('f1',), 60, 0, 15)
battlecry = Ability("Battle Cry", ('f2',), 45, 0, 10)
intimidating_shout = Ability("Intimidating Shout", ('f3',), 60, 0, 12)

# Groups
buffs = (powerhouse, battlecry, intimidating_shout)

# Combos
shield_slam = Combo("Shield Slam", ('g',), ["e", "2"], 9, 1)
shield_slam.should_weave = True

guard_destroyer = Combo("Guard Destroyer", ('4',), ["3"], 32, 1.5)

titanic_smash = Combo("Titanic Smash", ('t',), ["1", "2"], 20, 1)
titanic_smash.should_weave = True

titanic_smash_B = Combo("Titanic Smash (Buffs)", ('t',), ["1", "2"], 20, 1)
titanic_smash_B.attach_prefinishers(buffs)
titanic_smash_B.should_weave = True
titanic_smash_B.add_delay(2, .2)

counterweight = Combo("Counterweight", ('r',), ["2", "1"], 1, 2)
counterweight.should_weave = True

#counterweight_B = Combo("Counterweight (Buffed)", ('r',), ["2", "1"], "1", 1, 2, reckoning)
#counterweight_B.attach_prefinishers(buffs)
#counterweight_B.should_weave = True

overreachV = Combo("Overreach V", ('shift','r',), ["e", "1"], 1, 1.5)
overreachV.should_weave = True

overreachVI = Combo("Overreach VI", ('f',), ["2", "e", "1"], 1, 1.5)
overreachVI.should_weave = True

overreachVI_bv = Combo("Overreach VI", ('f',), ["2", "e", "1"], 1, 1.5, bloodyvengance)

combos = (breech,whirlwind,bloodbath,bloodyhack,whirlwind,bloodbath,bloodyhack,)
combos = combos + (whirlwind,bloodbath,bloodyhackV,)

# guard Rotation
""" combos = (
    shield_slam,
    guard_destroyer,
    titanic_smash,
    overreachV,
    shield_slam,
    overreachVI,
    overreachV,
    shield_slam,
    overreachV,
    titanic_smash,
    guard_destroyer,
    shield_slam,
    overreachV,
    overreachVI,
    shield_slam,
    titanic_smash,
    overreachV,
    )"""

#rotation1 = Rotation()
#rotation1.add_combo( breech, (1,) )
# Abilities at positions are stored as lists and are direct
# references to the original objects.
#rotation.add_ability( annihilate, (2,) )
#rotation1.add_ability( rend_flesh, (3,))
# Combos are added as copies of their originals, but the same copy is
# used for all positions requested.
#rotation1.add_combo( whirlwind, (2,5,9,) )
#rotation1.add_combo( bloodyhackV, (6,8,) )
#rotation1.add_combo( bloodbath, (3,7,) )
#rotation1.add_combo( bloodyhack, (4,) )

#rotation1.start()

rotation2 = Rotation()
rotation2.add_combo( guard_destroyer, (1,11) )
rotation2.add_combo( titanic_smash_B, (2,14) )
rotation2.add_combo( titanic_smash, (9,) )
rotation2.add_combo( counterweight, (3,6,10,13) )
rotation2.add_ability( reckoning, (4,7,11,14) )
#overreachVI.add_delay(2, .15)
rotation2.add_combo( overreachVI, (5,12,) )
rotation2.add_ability( bloodyvengance, (14,) )
rotation2.add_combo( overreachV, (4,8) )

keyboard.add_hotkey("1", rotation2.log_keypress, args=["UL attack key was pressed"])
keyboard.add_hotkey("2", rotation2.log_keypress, args=["MID attack key was pressed"])
keyboard.add_hotkey("3", rotation2.log_keypress, args=["UR for was pressed during"])
#keyboard.add_hotkey("q", rotation2.log_keypress, args=["LL for was pressed during"])
keyboard.add_hotkey("e", rotation2.log_keypress, args=["LR for was pressed during"])


def dump_key_event(event):
    print(event.event_type)
    print(event.name)
    print(event.scan_code)
    print(event.time)


def start_rotation(key_pressed):
    print('starting...')
    # change activation
    # keyboard.remove_hotkey(80)
    hk1 = keyboard.add_hotkey(key_pressed, rotation2.do_pause, args=[key_pressed])

    logging.debug('Preparing to start')

    r = threading.Timer(3, rotation2.start)
    r.start()
try:
    hk2 = keyboard.add_hotkey(80, start_rotation, args=[79])
    keyboard.wait('escape')

    # clean up the objects
    rotation2.end()
    AOC_lose_focus()
except Exception as e:
    print(e)
else:
    keyboard.unhook_all()

#if RUN_LEVEL == "DEBUG":
