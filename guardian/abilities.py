from ability import Ability
from ability import COOLDOWN_ACTIONS

class TacticProvoke(Ability):

    name = "Tactic: Provoke"
    cooldown_time = 0
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'q'
        self.modifier = 'ctrl'
        self.register_hotkey()


class TacticDefense(Ability):

    name = "Tactic: Defense"
    cooldown_time = 0
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'e'
        self.modifier = 'ctrl'
        self.register_hotkey()


class CryOfHavoc(Ability):

    name = "Rend Flesh"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT_SHORT

    def __init__(self):
        self.hotkey = 'q'
        self.register_hotkey()


class Irritate(Ability):

    name = "Irritate"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT
    use_on_cooldown = True

    def __init__(self):
        self.hotkey = 'z'
        self.register_hotkey()


class Powerhouse(Ability):

    name = "Powerhouse"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'F1'
        self.register_hotkey()


class BattleCry(Ability):

    name = "Battle Cry"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'F2'
        self.register_hotkey()


class CallToArms(Ability):

    name = "Call To Arms"
    cooldown_time = 45
    cooldown_action = COOLDOWN_ACTIONS.WAIT

    def __init__(self):
        self.hotkey = 'F3'
        self.register_hotkey()
