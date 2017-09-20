import math
from logging import getLogger

from simulation.utils.map_utils import UpdateMapAndAvatars
from simulation.action import MoveAction
from simulation.location import Location

LOGGER = getLogger(__name__)


DEFAULT_LEVEL_SETTINGS = {
    'TARGET_NUM_CELLS_PER_AVATAR': 0,
    'TARGET_NUM_SCORE_LOCATIONS_PER_AVATAR': 0,
    'SCORE_DESPAWN_CHANCE': 0,
    'TARGET_NUM_PICKUPS_PER_AVATAR': 0,
    'PICKUP_SPAWN_CHANCE': 0,
    'NO_FOG_OF_WAR_DISTANCE': 1000,
    'PARTIAL_FOG_OF_WAR_DISTANCE': 1000,
}


class Cell(object):
    """
    Any position on the world grid.
    """

    def __init__(self, location, habitable=True, generates_score=False, partially_fogged=False):
        self.location = location
        self.habitable = habitable
        self.generates_score = generates_score
        self.avatar = None
        self.pickup = None
        self.partially_fogged = partially_fogged
        self.actions = []

        # Used to update the map features in the current view of the user (score points on pickups).
        self.remove_from_scene = None
        self.add_to_scene = None

    def __repr__(self):
        return 'Cell({} h={} s={} a={} p={} f{})'.format(
            self.location, self.habitable, self.generates_score, self.avatar, self.pickup, self.partially_fogged)

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

    def serialise(self):
        if self.partially_fogged:
            return {
                'generates_score': self.generates_score,
                'location': self.location.serialise(),
                'partially_fogged': self.partially_fogged
            }
        else:
            return {
                'avatar': self.avatar.serialise() if self.avatar else None,
                'generates_score': self.generates_score,
                'habitable': self.habitable,
                'location': self.location.serialise(),
                'pickup': self.pickup.serialise() if self.pickup else None,
                'partially_fogged': self.partially_fogged
            }


class WorldMap(object):
    """
    The non-player world state.
    """

    def __init__(self, grid, settings):
        self.grid = grid
        self.settings = settings

    @classmethod
    def _min_max_from_dimensions(cls, height, width):
        max_x = int(math.floor(width / 2))
        min_x = -(width - max_x - 1)
        max_y = int(math.floor(height / 2))
        min_y = -(height - max_y - 1)
        return min_x, max_x, min_y, max_y

    @classmethod
    def generate_empty_map(cls, height, width, settings):
        new_settings = DEFAULT_LEVEL_SETTINGS.copy()
        new_settings.update(settings)

        (min_x, max_x, min_y, max_y) = WorldMap._min_max_from_dimensions(height, width)
        grid = {}
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                location = Location(x, y)
                grid[location] = Cell(location)
        return cls(grid, new_settings)

    def all_cells(self):
        return self.grid.itervalues()

    # Used to know when to instantiate objects in the scene.
    def cells_to_create(self):
        new_cells = []
        for cell in self.all_cells():
            if not cell.created:
                new_cells.append(cell)
        return new_cells

    # TODO: Cells to delete

    def score_cells(self):
        return (c for c in self.all_cells() if c.generates_score)

    def potential_spawn_locations(self):
        return (c for c in self.all_cells()
                if c.habitable
                and not c.generates_score
                and not c.avatar
                and not c.pickup)

    def pickup_cells(self):
        return (c for c in self.all_cells() if c.pickup)

    def is_on_map(self, location):
        try:
            self.grid[location]
        except KeyError:
            return False
        return True

    def get_cell(self, location):
        try:
            return self.grid[location]
        except KeyError:
            # For backwards-compatibility, this throws ValueError
            raise ValueError('Location %s is not on the map' % location)

    def get_cell_by_coords(self, x, y):
        return self.get_cell(Location(x, y))

    def clear_cell_actions(self, location):
        try:
            cell = self.get_cell(location)
            cell.actions = []
        except ValueError:
            return

    def max_y(self):
        return max(self.grid.keys(), key=lambda c: c.y).y

    def min_y(self):
        return min(self.grid.keys(), key=lambda c: c.y).y

    def max_x(self):
        return max(self.grid.keys(), key=lambda c: c.x).x

    def min_x(self):
        return min(self.grid.keys(), key=lambda c: c.x).x

    @property
    def num_rows(self):
        return self.max_y() - self.min_y() + 1

    @property
    def num_cols(self):
        return self.max_x() - self.min_x() + 1

    @property
    def num_cells(self):
        return self.num_rows * self.num_cols

    def update(self, num_avatars):
        """
            Calls a separate utility class which handles all the updates.
            All logic was refactored from here to UpdateMapAndAvatars.

            :param self: The world_map object
            :param num_avatars: The new number of avatars
        """
        UpdateMapAndAvatars.update_avatars_and_map(self, num_avatars)

    def get_random_spawn_location(self):
        """
        Return a single random spawn location.

        Throws:
            IndexError: if there are no possible locations.
        """
        return UpdateMapAndAvatars.get_random_spawn_locations_external(self, 1)[0].location

    def can_move_to(self, target_location):
        if not self.is_on_map(target_location):
            return False
        cell = self.get_cell(target_location)

        return (cell.habitable
                and (not cell.is_occupied or cell.avatar.is_moving)
                and len(cell.moves) <= 1)

    def attackable_avatar(self, target_location):
        """
        Return the avatar attackable at the given location, or None.
        """
        try:
            cell = self.get_cell(target_location)
        except ValueError:
            return None

        if cell.avatar:
            return cell.avatar

        if len(cell.moves) == 1:
            return cell.moves[0].avatar

        return None

    def get_no_fog_distance(self):
        return self.settings['NO_FOG_OF_WAR_DISTANCE']

    def get_partial_fog_distance(self):
        return self.settings['PARTIAL_FOG_OF_WAR_DISTANCE']

    def __repr__(self):
        return repr(self.grid)

    def __iter__(self):
        return ((self.get_cell(Location(x, y))
                for y in range(self.min_y(), self.max_y() + 1))
                for x in range(self.min_x(), self.max_x() + 1))


def world_map_static_spawn_decorator(world_map, spawn_location):
    world_map.get_random_spawn_location = lambda: spawn_location
    return world_map
