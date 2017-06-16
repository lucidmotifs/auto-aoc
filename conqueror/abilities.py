from ability import Ability
from ability import COOLDOWN_ACTIONS

class Annihilate(Ability):

    name = "Annihilate"
    cooldown_time = 180
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        self.hotkey = '9'
        self.register_hotkey()


class RendFlesh(Ability):

    name = "Rend Flesh"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT_SHORT

    def __init__(self):
        self.hotkey = '0'
        self.register_hotkey()


class BladeWeave(Ability):

    name = "Blade Weave"
    cooldown_time = 20
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        self.hotkey = 'f1'
        self.register_hotkey()


class PlantBanner(Ability):

    name = "Plant Banner"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'f3'
        self.register_hotkey()


class UseDiscipline(Ability):

    name = "Use Discipline"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT_SHORT

    def __init__(self):
        self.hotkey = 'f2'
        self.register_hotkey()
