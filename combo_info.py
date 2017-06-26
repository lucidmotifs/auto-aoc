# general utltily
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


logging.basicConfig(
    format='(%(threadName)-10s) %(asctime)s.%(msecs)03d %(message)s',
    datefmt = '%M:%S',
    filename='testing.log',
    filemode='w',
    level=logging.DEBUG)


def test_random_combo(rotation):
    combo = rotation.get_combo_at( \
                random.randrange(1, max(rotation.actions.keys())))

    print("Printing Details for {}".format(combo.name))
    print("Hotkey: {}".format(combo.hotkey))
    print("Queue: {}".format(combo.schedule))
    print("Cooldown Time: {}".format(combo.cooldown_time))
    print("Cast Time: {}".format(combo.cast_time))

    if combo.modifier:
        print("Modifier {}".format(combo.modifier))
    else:
        print("No Modifier")

    print("Testing Keypress")
    combo.print_keyevents()

    print("Testing KEYBINDS")
    #generic._set_focus()
    #time.sleep(1)
    #pyautogui.typewrite('q123e', .5)
    print("Done. Check output.txt")

    #print("Testing Cooldown")
    #combo.init_cooldown()

    print("Testing Simulation")
    combo.use()
    time.sleep(combo.cast_time)

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


from rotations import Guardian_DPS as gdps

r = Rotation()
generic.register_keybinds(r)
r = gdps()

## Just a combo
test_random_combo(r)
#keyboard.unhook_all()

## Combo and ability
test_random_combo(r)
test_random_ability(r)
keyboard.unhook_all()
