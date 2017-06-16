# gneral utltily
import logging
import random
import generic
import time

# keyboard hooks
import keyboard
import pyautogui
import pywinauto

# timing module
from timeit import default_timer as timer

# from this application
from rotation import Rotation
from ability import Ability
from ability import COOLDOWN_ACTIONS
from combo import Combo

# classes and combos
from conqueror.combos import *
from conqueror.abilities import *


logging.basicConfig(
    format='%(message)s',
    filename='output.txt',
    filemode='w',
    level=logging.DEBUG)


def test_random_combo(rotation):
    combo = rotation.get_combo_at( \
                random.randrange(1, max(rotation.actions.keys())))

    print("Printing Details for {}".format(combo.name))
    print("Hotkey: {}".format(combo.hotkey))
    print("Word: {}".format(combo.word))
    print("Cooldown Time: {}".format(combo.cooldown_time))
    print("Cast Time: {}".format(combo.cast_time))

    if combo.modifier:
        print("Modifier {}".format(combo.modifier))
    else:
        print("No Modifier")

    print("Testing Keypress")
    combo.print_keyevents()

    print("Testing KEYBINDS")
    generic.register_keybinds(rotation)
    generic._set_focus()
    time.sleep(1)
    pyautogui.typewrite('q123e', .5)
    print("Done. Check output.txt")

    print("Testing Cooldown")
    combo.init_cooldown()

    time.sleep(combo.cooldown_time)

    print("Testing Simulation")
    combo.simluate_keyevents()

def test_random_ability(rotation):
    ability = \
        rotation.ability_list[random.randrange(0, len(rotation.ability_list))]

    print("Printing Details for {}".format(ability.name))
    print("Hotkey: {}".format(ability.hotkey))
    print("Cooldown Time: {}".format(ability.cooldown_time))

    if ability.modifier:
        print("Modifier {}".format(ability.modifier))
    else:
        print("No Modifier")

    print("Testing Keypress")
    ability.use()

    time.sleep(5)

    print("Testing on_cooldown reaction")
    ability.use()

    time.sleep(1)
    ability.cooldown.cancel()


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

conq_dps.print_rotation()

test_random_combo(conq_dps)
test_random_ability(conq_dps)

keyboard.unhook_all()
