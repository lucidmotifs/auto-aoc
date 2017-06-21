from ability import Ability
from ability import COOLDOWN_ACTIONS

class TacticProvoke(Ability):

    def __init__(self):
        super().__init__("Tactic: Provoke", 0)
        self.hotkey = 'q'
        self.modifier = 'ctrl'


class TacticDefense(Ability):

    def __init__(self):
        super().__init__("Tactic: Defense", 0)
        self.hotkey = 'e'
        self.modifier = 'ctrl'


class CryOfHavoc(Ability):

    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = True

    def __init__(self):
        super().__init__("Cry of Havoc", 15.0)
        self.hotkey = 'q'


class Irritate(Ability):

    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = True

    def __init__(self):
        super().__init__("Irritate", 20.0)
        self.hotkey = 'z'


class Powerhouse(Ability):

    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        super().__init__("Powerhouse", 60.0)
        self.hotkey = 'f1'


class BattleCry(Ability):

    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        super().__init__("Battle Cry", 45.0)
        self.hotkey = 'f2'


class CallToArms(Ability):

    cooldown_action = COOLDOWN_ACTIONS.SKIP

    def __init__(self):
        super().__init__("Call To Arms", 60.0)
        self.hotkey = 'f3'


class BloodyVegeance(Ability):

    cooldown_action = COOLDOWN_ACTIONS.SKIP
    cast_time = 1.5

    def __init__(self):
        super().__init__("Bloody Vegeance", 27.0, 1.5)
        self.hotkey = '5'


class Reckoning(Ability):
    cooldown_action = COOLDOWN_ACTIONS.RETRY
    use_on_cooldown = False

    def __init__(self):
        super().__init__("Reckoning", 10.0)
        self.hotkey = 'q'
