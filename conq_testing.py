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

logging.basicConfig(
    format='(%(threadName)-10s) %(message)s'
    filename='output.txt',
    filemode='w',
    level=logging.DEBUG)

_set_focus()

## Conqueror DPS Rotation
conq_dps = Rotation()

# Combos
conq_dps.use( Breech(4) ).at( 1 )
conq_dps.use( Whirlwind() ).at( 2, 6 )
conq_dps.use( BloodyHack(6) ).at( 3 )
conq_dps.use( BloodyHack(5) ).at( 5, 7 )
conq_dps.use( Bloodbath(6) ).at( 4, 8 )

# Abilities
conq_dps.use( BladeWeave() ).at( 1 )
conq_dps.use( UseDiscipline() ).at( 2 )
conq_dps.use( Annihilate() ).at( 3 )
conq_dps.use( RendFlesh() ).at( 4 )

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

overreachV = Combo("Overreach V", '8', ["e", "1"], 1, 1.5)

overreachVI = Combo("Overreach VI", 'f', ["2", "e", "1"], 1, 1.5)
overreachVI.should_weave = True

overreachVI_bv = Combo("Overreach VI", 'f', ["2", "e", "1"], 1, 1.5, bloodyvengance)

# Guard Aggro Rotation
combos = (q
    1shield_slam,
    tactic_provoke,
    cry_of_havoc,
    irritate,
     ,
    3titanic_smash_B,
    4overreachV,
    5shield_slam,
    6overreachVI,
    7overreachV,
    8shield_slam,
    9overreachV,
    cry_of_havoc,
    10titanic_smash,
    11guard_destroyer,
    12shield_slam,
    13overreachV,
    14overreachVI,
    15shield_slam,
    16titanic_smash,
    17overreachV,
    tactic_defense,
)

aggro = Rotation()
aggro.add( combos )


def start_rotation2(rotation, pause_key):
    generic.register_keybinds(rotation)

    print('Starting...')
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
except Exception as e:
    print(e)
else:
    keyboard.unhook_all()
    generic._lose_focus()

#if RUN_LEVEL == "DEBUG":
