import math
import random
from logging import getLogger

from simulation.maps.cell import Cell
from simulation.world_state import MapFeature
from simulation.pickups import ALL_PICKUPS
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
        for x in xrange(min_x, max_x + 1):
            for y in xrange(min_y, max_y + 1):
                location = Location(x, y)
                grid[location] = Cell(location)
        return cls(grid, new_settings)

    def all_cells(self):
        return self.grid.itervalues()

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
        self._add_pickups(num_avatars)

    def _add_pickups(self, num_avatars):
        for cell in self.pickup_cells():
            if cell.avatar is not None:
                cell.pickup.apply(cell.avatar)

        target_num_pickups = int(math.ceil(num_avatars * self.settings['TARGET_NUM_PICKUPS_PER_AVATAR']))
        LOGGER.debug('Aiming for %s new pickups', target_num_pickups)
        max_num_pickups_to_add = target_num_pickups - len(list(self.pickup_cells()))
        locations = self._get_random_spawn_locations(max_num_pickups_to_add)
        for cell in locations:
            if random.random() < self.settings['PICKUP_SPAWN_CHANCE']:
                LOGGER.info('Adding new pickup at %s', cell)
                cell.pickup = random.choice(ALL_PICKUPS)(cell)

    def _get_random_spawn_locations(self, max_locations):
        if max_locations <= 0:
            return []
        potential_locations = list(self.potential_spawn_locations())
        try:
            return random.sample(potential_locations, max_locations)
        except ValueError:
            LOGGER.debug('Not enough potential locations')
            return potential_locations

    def get_random_spawn_location(self):
        """Return a single random spawn location.

        Throws:
            IndexError: if there are no possible locations.
        """
        return self._get_random_spawn_locations(1)[0].location

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

    def __repr__(self):
        return repr(self.grid)

    def __iter__(self):
        return ((self.get_cell(Location(x, y))
                 for y in xrange(self.min_y(), self.max_y() + 1))
                for x in xrange(self.min_x(), self.max_x() + 1))


def world_map_static_spawn_decorator(world_map, spawn_location):
    world_map.get_random_spawn_location = lambda: spawn_location
    return world_map
