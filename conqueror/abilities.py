class Annihilate(Ability):

    name = "Annihilate"
    cooldown_time = 180
    

    def __init__(self, rank=4):
        self.set_rank(rank)
        self.hotkey = '4'

    def set_rank(self, rank):
        self.steps = ["3"]

        if rank is 4:
            self.name = "Breech IV"
            self.cast_time = 1.5
