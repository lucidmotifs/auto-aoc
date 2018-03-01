import logging

from collections import deque
from combo import Combo
from ability import Ability


class Rotation():

    deck = deque()

    def use(self, action):
        """
        This method is designed for fully formed combos that manage their
        own hotkey callbacks and doesn't require a copy to be made.
        """
        if isinstance(action, Combo):
            if action not in self.combo_list:
                self.combo_list.append(action)
        elif isinstance(action, Ability):
            if action not in self.ability_list:
                self.ability_list.append(action)
        else:
            logging.debug("Invalid action passed to Rotation")

    def add(self, round):
        self.deck.append(round)

    def get_combo_at(self, position):
        try:
            combo = (i for i in self.deck[position] if isinstance(i, Combo))
            return next(combo)
        except StopIteration as e:
            return None

    def print_rotation(self):
        """
        Print a string representation of the actions associated with this
        roatation. If this is a priority-based rotation, show the next 10
        items.
        """
        pass

    def __str__(self):
        """
        Returns as a string the 'word' for the current rotation queue.
        """
        word = list()
        for i, actions in sorted(self.actions.items()):
            for a in actions:
                word.append(a.word)

        return ''.join(word)
