from simulation.action import MoveAction


class Cell(object):
    """
    Any position on the world grid.
    """

    def __init__(self, location, habitable=True):
        self.location = location
        self.habitable = habitable
        self.avatar = None
        self.pickup = None
        self.actions = []

    def __repr__(self):
        return 'Cell({} h={} a={} p={})'.format(
            self.location, self.habitable, self.avatar, self.pickup)

    def __eq__(self, other):
        return self.location == other.location

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.location)

    @property
    def moves(self):
        return [move for move in self.actions if isinstance(move, MoveAction)]

    @property
    def is_occupied(self):
        return self.avatar is not None