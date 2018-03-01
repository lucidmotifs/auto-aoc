from ability import Ability
from ability import cooldown_actions

class TacticProvoke(Ability):

    def __init__(self):
        super().__init__("Tactic: Provoke", 0)
        self.modifier = 'ctrl'
        self.hotkey = 'q'


class TacticDefense(Ability):

    def __init__(self):
        super().__init__("Tactic: Defense", 0)
        self.modifier = 'ctrl'
        self.hotkey = 'e'


class CryOfHavoc(Ability):

    cooldown_action = cooldown_actions.SKIP
    use_on_cooldown = True

    def __init__(self):
        super().__init__("Cry of Havoc", 15.0)
        self.hotkey = 'q'


class Irritate(Ability):

    cooldown_action = cooldown_actions.WAIT
    use_on_cooldown = True

    def __init__(self):
        super().__init__("Irritate", 20.0)
        self.hotkey = 'z'


class Powerhouse(Ability):

    cooldown_action = cooldown_actions.SKIP

    def __init__(self):
        super().__init__("Powerhouse", 60.0)
        self.hotkey = 'f1'


class BattleCry(Ability):

    cooldown_action = cooldown_actions.SKIP

    def __init__(self):
        super().__init__("Battle Cry", 45.0)
        self.hotkey = 'f2'


class CallToArms(Ability):

    cooldown_action = cooldown_actions.SKIP

    def __init__(self):
        super().__init__("Call To Arms", 60.0)
        self.hotkey = 'f3'


class BloodyVengeance(Ability):

    cooldown_action = cooldown_actions.SKIP
    cast_time = 1.5

    def __init__(self):
        super().__init__("Bloody Vengeance", 27.0, 1.5)
        self.hotkey = '5'


class Reckoning(Ability):
    cooldown_action = cooldown_actions.SKIP
    use_on_cooldown = False

    def __init__(self):
        super().__init__("Reckoning", 10.0)
        self.hotkey = 'q'
