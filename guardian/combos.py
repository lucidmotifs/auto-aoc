from combo import Combo

class GuardDestroyer(Combo):

    name = "Guard Destroyer"
    cooldown_time = 32.0

    def __init__(self, rank=4):
        self.set_factory_defaults()
        self.set_rank(rank)
        self.hotkey = '4'
        self.build_word()

    def set_rank(self, rank):
        self.steps = ["3"]

        if rank is 4:
            self.name += " IV"
            self.cast_time = 1.5


class Counterweight(Combo):

    name = "Counterweight"
    cooldown_time = 2.0

    # Counterweight has only one rank, set cast time here
    cast_time = 2
    steps = ["2","1"]

    def __init__(self):
        self.set_factory_defaults()
        self.hotkey = 'r'
        self.build_word()


class TitanicSmash(Combo):

    name = "Titanic Smash"
    cooldown_time = 20

    # TitanicSmash has only one rank, set cast time here
    cast_time = 1
    steps = ["1","2"]

    def __init__(self):
        self.set_factory_defaults()
        self.hotkey = 't'
        self.build_word()


class Overreach(Combo):

    name = "Overreach"
    cooldown_time = 2.0

    def __init__(self, rank=6):
        self.set_factory_defaults()
        self.set_rank(rank)
        self.build_word()


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

    name = "Shield Slam"
    cooldown_time = 9.0

    # TitanicSmash has only one rank, set cast time here
    cast_time = 1.0
    steps = ["e","2"]

    def __init__(self):
        self.set_factory_defaults()
        self.hotkey = 'g'
        self.build_word()
