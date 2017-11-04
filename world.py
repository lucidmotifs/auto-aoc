import logging


class World():

    combos = []
    abilities = []
    spells = []

    _current_action = None

    @classmethod
    def print_current_cooldowns(cls):
        logging.debug("Abilities Status:")
        [a.status() for a in cls.abilities]
        logging.debug("Combo Status:")
        [c.status() for c in cls.combos]

        try:
            logging.debug("Post Abilities:")
            [ability.status() for ability in
             [a for a in
              [a for a in
               [c.post_finishers for c in cls.combos
                if c.post_finishers is not None]] if len(a) is not 0][0]]
        except IndexError:
            logging.debug("No Post-Finisher abilities")

        try:
            logging.debug("Pre-finisher Abilities:")
            [ability.status() for ability in
             [a for a in
              [a for a in
               [c.pre_finishers for c in cls.combos
                if c.pre_finishers is not None]] if len(a) is not 0][0]]
        except IndexError:
            logging.debug("No Pre-Finisher abilities")

    @classmethod
    def cancel_current_cooldown(cls):
        # check repeat options, see many time we've run the Rotation
        # use a filler to get a CD or buff back, potentially. Even a single
        # repeat_until rotation of simple combos.
        [i.cooldown.cancel() for i in cls.ability_list
         if i.cooldown is not None]

        [[i.cooldown.cancel() for i in x if i.cooldown is not None] for x in
         [j.pre_finishers for j in cls.combo_list]]

        [i.cooldown.cancel() for i in cls.combo_list if i.cooldown is not None]
