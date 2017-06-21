from ability import Ability
from ability import COOLDOWN_ACTIONS

class Annihilate(Ability):

    name = "Annihilate"
    cooldown_time = 180
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        super().__init__( "Annihilate", 180.0 )
        self.hotkey = '9'


class RendFlesh(Ability):

    name = "Rend Flesh"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT_SHORT

    def __init__(self):
        super().__init__(
            "Rend Flesh",
            45.0

        )
        self.hotkey = '0'


class BladeWeave(Ability):

    name = "Blade Weave"
    cooldown_time = 20
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        super().__init__(
            "Blade Weave",
            20.0
        )
        self.hotkey = 'f1'


class PlantBanner(Ability):

    name = "Plant Banner"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        super().__init__(
            "Plant Banner",
            45.0
        )
        self.hotkey = 'f3'


class UseDiscipline(Ability):

    name = "Use Discipline"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT_SHORT

    def __init__(self):
        super().__init__(
            "Use Discipline",
            45.0
        )
        self.hotkey = 'f2'
