from combo import Combo
from conqueror.abilities import *

class GuardDestroyer(Combo):

    def __init__(self, rank=4):
        self.set_rank(4)
        super().__init__("Guard Destroyer",
                         32,
                         self.cast_time)

        self.hotkey = '4'

    def set_rank(self, rank):
        self.steps = ["3"]

        if rank is 4:
            self.name += " IV"
            self.cast_time = 1.5


class Counterweight(Combo):

    # Counterweight has only one rank, set cast time here
    steps = ["2","1"]

    def __init__(self):
        super().__init__("Counterweight",
                         "cooldown_time" = 2.0,
                         "cast_time" = 2.0)

        self.hotkey = 'r'


class TitanicSmash(Combo):

    # TitanicSmash has only one rank, set cast time here
    steps = ["1","2"]

    def __init__(self):
        super().__init__("Titanic Smash",
                         20,
                         1.0)

        self.hotkey = 't'


class Overreach(Combo):

    name = "Overreach"
    cooldown_time = 2.0

    def __init__(self, rank=6):
        self.set_rank(rank)
        def __init__(self):
            super().__init__(self.name,
                             2.0,
                             self.cast_time)


    def set_rank(self, rank):

        if rank is 6:
            self.name += " VI"
            self.hotkey = 'f'
            self.cast_time = 1.5
            self.steps = ["2","e","1"]
        if rank is 5:
            self.name += " V"
            self.hotkey = '8'
            self.cast_time = 1.5
            self.steps = ["e","1"]


class ShieldSlam(Combo):

    steps = ["e","2"]

    def __init__(self):
        super().__init__("Shield Slam",
                         9.0,
                         1.0)

        self.hotkey = 'g'


class DullingBlow(Combo):

    def __init__(self, rank=4):
        self.set_rank(rank)
        super().__init__("Dulling Blow",
                         9.0,
                         self.cast_time)


    def set_rank(self, rank):
        if rank is 4:
            self.name += " IV"
            self.hotkey = '6'
            self.steps = ["3"]
            self.cast_time = 1.0
