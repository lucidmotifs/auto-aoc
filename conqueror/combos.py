class Breech(Combo):

    name = "Breech"
    cooldown_time = 41.0

    def __init__(self, rank=4):
        self.set_rank(rank)

    def set_rank(self, rank):
        self.steps = ["3"]

        if rank is 4:
            self.cast_time = 1.5
