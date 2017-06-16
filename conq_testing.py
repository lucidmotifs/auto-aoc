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
from rotation import Rotation
from ability import Ability
from ability import COOLDOWN_ACTIONS
from combo import Combo

# classes and combos
from conqueror.combo import *


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
#PROCNAME = "notepad.exe"

logging.basicConfig(
    format='%(message)s',
    filename='output.txt',
    filemode='w',
    level=logging.DEBUG)

def AOC_set_focus():
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            PID = proc.pid

    app = application.Application()
    app = app.connect(process=PID)
    window = app.top_window_()
    window.Minimize()
    window.Restore()
    window.SetFocus()

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


if RUN_LEVEL == "TESTING":
    AOC_set_focus()
elif RUN_LEVEL == "PROD":
    # assume we're running from in-game
    time.sleep(100)

## Conqueror DPS Rotation
conq_dps = Rotation()

# Combos
conq_dps.use( Breech(4) ).at( 1 )
conq_dps.use( Whirlwind() ).at( 2, 6 )
conq_dps.use( BloodyHack(5) ).at( 3, 5, 7 )
conq_dps.use( Bloodbath(6) ).at( 4 )

# Abilities

# Add a 300ms to the first step
# bloodyhackV.add_delay(1, .1)
# whirlwind.add_delay(1, .2)

#annihilate = Ability("Annihilate", ('5',), 180, 0, 20)
#rend_flesh = Ability("Rend Flesh", ('g',), 60, 0, 20)

# Abilities
bloodyvengance = Ability("Bloody Vengeance", '5', 27, 1.5, 0)
reckoning = Ability("Reckoning", 'q', 10, 0, 0)
powerhouse = Ability("Powerhouse", 'f1', 60, 0, 15)
battlecry = Ability("Battle Cry", 'f2', 45, 0, 10)
intimidating_shout = Ability("Intimidating Shout", 'f3', 60, 0, 12)
tactic_provoke = Ability("Tactic: Provoke", 'e', 0, 0, 0)
tactic_provoke.modifier = 'ctrl'
tactic_defense = Ability("Tactic: Defense", 'q', 0, 0, 0)
tactic_defense.modifier = 'ctrl'
cry_of_havoc = Ability("Cry of Havok", 'q', 15, 0, 0)
irritate = Ability("Irritate", 'z', 20, 0, 0)
switch_weapons = Ability("Switch Weapons", 'Z', 0, 0, 0)

# Groups
buffs = (powerhouse, battlecry, intimidating_shout)

# Combos
shield_slam = Combo("Shield Slam", 'g', ["e", "2"], 9, 1)

dulling_blow = Combo("Dulling Blow", '6', ["3"], 9, 1)

guard_destroyer = Combo("Guard Destroyer", '4', ["3"], 32, 1.5)

titanic_smash = Combo("Titanic Smash", 't', ["1", "2"], 20, 1)

titanic_smash_B = Combo("Titanic Smash (Buffs)", 't', ["1", "2"], 20, 1)
titanic_smash_B.attach_prefinishers(buffs)

counterweight = Combo("Counterweight", 'r', ["2", "1"], 1, 2)
counterweight.should_weave = True

#counterweight_B = Combo("Counterweight (Buffed)", ('r',), ["2", "1"], "1", 1, 2, reckoning)
#counterweight_B.attach_prefinishers(buffs)
#counterweight_B.should_weave = True

overreachV = Combo("Overreach V", '8', ["e", "1"], 1, 1.5)

overreachVI = Combo("Overreach VI", 'f', ["2", "e", "1"], 1, 1.5)
overreachVI.should_weave = True

overreachVI_bv = Combo("Overreach VI", 'f', ["2", "e", "1"], 1, 1.5, bloodyvengance)

# guard Rotation
combos = (
    shield_slam,
    tactic_provoke,
    cry_of_havoc,
    irritate,
    guard_destroyer,
    titanic_smash_B,
    overreachV,
    shield_slam,
    overreachVI,
    overreachV,
    shield_slam,
    overreachV,
    cry_of_havoc,
    titanic_smash,
    guard_destroyer,
    shield_slam,
    overreachV,
    overreachVI,
    shield_slam,
    titanic_smash,
    overreachV,
    tactic_defense,
)

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

'''rotation2 = Rotation()
rotation2.add_combo( guard_destroyer, (1,11) )
rotation2.add_combo( titanic_smash_B, (2,14) )
rotation2.add_combo( titanic_smash, (9,) )
rotation2.add_combo( counterweight, (3,6,10,13) )
rotation2.add_ability( reckoning, (4,7,11,14) )
#overreachVI.add_delay(2, .15)
rotation2.add_combo( overreachVI, (5,12,) )
rotation2.add_ability( bloodyvengance, (14,) )
rotation2.add_combo( overreachV, (4,8) )'''

rot = Rotation()
rot.add_combo( guard_destroyer, (1,10))
rot.add_combo( titanic_smash_B, (2,19))
rot.add_combo( counterweight, (3,5,8,11,14,17))
rot.add_combo( overreachVI, (4,6,15,))
rot.add_combo( titanic_smash, (7,13,))
rot.add_combo( overreachV, (12,16,18))
rot.add_combo( dulling_blow, (9,19))

rot.add_ability( bloodyvengance, (4,11))
rot.add_ability( reckoning, (4,6,9,12,15,18))
rot.add_ability( switch_weapons, (19,))


rot.repeat = True
rot.repeat_count = 0

grd_dps = rot

aggro = Rotation()
aggro.add( combos )


def register_attack_keys(rotation):
    keyboard.add_hotkey("1", rotation.log_keypress, \
        args=["UL attack key was pressed"])
    keyboard.add_hotkey("2", rotation.log_keypress, \
        args=["MID attack key was pressed"])
    keyboard.add_hotkey("3", rotation.log_keypress, \
        args=["UR for was pressed during"])
    keyboard.add_hotkey("q", rotation.log_keypress, \
        args=["LL for was pressed during"])
    keyboard.add_hotkey("e", rotation.log_keypress, \
        args=["LR for was pressed during"])


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


def start_rotation(key_pressed):
    print('starting...')
    # change activation
    # keyboard.remove_hotkey(80)
    hk1 = keyboard.add_hotkey(key_pressed, rot.do_pause, args=[key_pressed])
    #LAST_KEY_EVENT = 0.0
    #hk2 = keyboard.hook(dump_key_event)

    logging.debug('Preparing to start')

    r = threading.Timer(0.1, rot.start)
    r.start()


def start_rotation2(rotation, pause_key):
    register_attack_keys(rotation)

    print('starting...')
    # change activation
    # keyboard.remove_hotkey(80)
    hk1 = keyboard.add_hotkey(pause_key, rotation.do_pause, args=[pause_key])

    logging.debug('Preparing to start')

    r = threading.Timer(0.1, rotation.start)
    r.start()


try:
    hk2 = keyboard.add_hotkey(80, start_rotation2, args=[grd_dps, 79])
    hk3 = keyboard.add_hotkey(81, start_rotation2, args=[aggro, 79])
    hk4 = keyboard.add_hotkey(75, start_rotation2, args=[conq_dps, 79])
    hk5 = keyboard.add_hotkey('-', dump_keys)
    keyboard.wait('escape')

    # clean up the objects
    # rot.end()
except Exception as e:
    print(e)
else:
    keyboard.unhook_all()
    AOC_lose_focus()

#if RUN_LEVEL == "DEBUG":
