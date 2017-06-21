from combo import Combo

## DW_ATK_INT
DW_ATK_INT = .65

class Breech(Combo):

    attack_interval = DW_ATK_INT

    def __init__(self, rank=4):
        super().__init__("Breech", 41.0)
        self.set_rank(rank)
        self.hotkey = '4'

    def set_rank(self, rank):
        self.steps = ["1"]

        if rank is 4:
            self.name = "Breech IV"
            self.cast_time = 1.5


class Whirlwind(Combo):

    attack_interval = DW_ATK_INT

    # Whirlwind has only one rank, set cast time here
    cast_time = 1.5
    steps = ["e","q","3"]

    def __init__(self):
        super().__init__("Whirlwind", 10.0)
        self.hotkey = 'r'


class BloodyHack(Combo):

    attack_interval = DW_ATK_INT

    def __init__(self, rank=6):
        super().__init__("Blood Hack", 2.0)
        self.set_rank(rank)


    def set_rank(self, rank):

        if rank is 6:
            self.name += " VI"
            self.hotkey = 'f'
            self.cast_time = 1.5
            self.steps = ["2","q","3"]
        if rank is 5:
            self.name += " V"
            self.hotkey = '5'
            self.cast_time = 1
            self.steps = ["2","3"]


class Bloodbath(Combo):

    attack_interval = DW_ATK_INT

    def __init__(self, rank=6):
        super().__init__("Bloodbath", 10.0)
        self.set_rank(rank)


    def set_rank(self, rank):

        if rank is 6:
            self.name = "Bloodbath VI"
            self.hotkey = 't'
            self.cast_time = 2
            self.steps = ["q","e","2"]
        if rank is 5:
            self.name = "Bloody Hack V"
            self.hotkey = '7'
            self.cast_time = 1.5
            self.steps = ["e","2"]
