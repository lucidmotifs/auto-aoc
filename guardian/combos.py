class GuardDestroyer(Combo):

    def __init__(self, rank=4):
        super().__init__("Breech", "4", self.get_steps(rank), self.finisher, 43, 1.5, post_ability=None)
        self.step_delays = {}


    def get_steps(self, rank):
        self.steps = []
        self.finisher = "3"
        self.execute_time = 1.0

        return self.steps
