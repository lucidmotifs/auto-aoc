class Breech(Combo):

    name = "Breech"
    cooldown_time = 41.0

    def __init__(self, rank=4):
        self.set_rank(rank)
        self.hotkey = '4'

    def set_rank(self, rank):
        self.steps = ["3"]

        if rank is 4:
            self.name = "Breech IV"
            self.cast_time = 1.5


class Whirlwind(Combo):

    name = "Whirlwind"
    cooldown_time = 10.0

    # Whirlwind has only one rank, set cast time here
    cast_time = 1.5
    steps = ["e","q","3"]

    def __init__(self):
        self.hotkey = 'r'
        self.build_word()


class BloodyHack(Combo):

    name = "Bloody Hack"
    cooldown_time = 2.0

    def __init__(self, rank=6):
        self.set_rank(rank)
        self.build_word()


    def set_rank(self, rank):

        if rank is 6:
            self.name = "Bloody Hack VI"
            self.hotkey = 'f'
            self.cast_time = 1.5
            self.steps = ["2","q","3"]
        if rank is 5:
            self.name = "Bloody Hack V"
            self.hotkey = '5'
            self.cast_time = 1
            self.steps = ["2","3"]


class Bloodbath(Combo):

    name = "Bloodbath"
    cooldown_time = 10.0

    def __init__(self, rank=6):
        self.set_rank(rank)


    def set_rank(self, rank):

        if rank is 6:
            self.name = "Bloodbath VI"
            self.hotkey = 't'
            self.cast_time = 2
            self.steps = ["2","q","3"]
        if rank is 5:
            self.name = "Bloody Hack V"
            self.hotkey = '7'
            self.cast_time = 1.5
            self.steps = ["e","2"]
