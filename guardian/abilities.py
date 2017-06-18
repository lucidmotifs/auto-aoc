from ability import Ability
from ability import COOLDOWN_ACTIONS

class TacticProvoke(Ability):

    name = "Tactic: Provoke"
    cooldown_time = 0

    def __init__(self):
        self.hotkey = 'q'
        self.modifier = 'ctrl'
        self.register_hotkey()


class TacticDefense(Ability):

    name = "Tactic: Defense"
    cooldown_time = 0

    def __init__(self):
        self.hotkey = 'e'
        self.modifier = 'ctrl'
        self.register_hotkey()


class CryOfHavoc(Ability):

    name = "Rend Flesh"
    cooldown_time = 15.0
    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = True

    def __init__(self):
        self.hotkey = 'q'
        self.register_hotkey()


class Irritate(Ability):

    name = "Irritate"
    cooldown_time = 20.0
    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = True

    def __init__(self):
        self.hotkey = 'z'
        self.register_hotkey()


class Powerhouse(Ability):

    name = "Powerhouse"
    cooldown_time = 60.0
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        self.hotkey = 'F1'
        self.register_hotkey()


class BattleCry(Ability):

    name = "Battle Cry"
    cooldown_time = 45.0
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        self.hotkey = 'F2'
        self.register_hotkey()


class CallToArms(Ability):

    name = "Call To Arms"
    cooldown_time = 60.0
    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        self.hotkey = 'F3'
        self.register_hotkey()


class BloodyVegeance(Ability):

    name = "Bloody Vegeance"
    cooldown_time = 27.0
    cooldown_action = COOLDOWN_ACTIONS.SKIP
    cast_time = 1.5

    def __init__(self):
        self.hotkey = '5'
        self.register_hotkey()


class Reckoning(Ability):

    name = "Reckoning"
    cooldown_time = 10.0
    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = False

    def __init__(self):
        self.hotkey = 'q'
        self.register_hotkey()
