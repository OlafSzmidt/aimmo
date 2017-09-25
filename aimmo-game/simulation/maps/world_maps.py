import random
from logging import getLogger

from simulation.location import Location

LOGGER = getLogger(__name__)


class WorldMaps(object):
    '''
    The representation of the world. All modification logic should be
    placed elsewhere in the package.
    '''

    def __init__(self, grid, settings):
        self.grid = grid
        self.settings = settings

    def all_cells(self):
        '''
        Written to support both python3 and python2. itervalues() became obsolete
        in py3 and values() returns dictionary views, which are iterators.
        :return: Iterator (dictionary or iterator) of all cells in the grid.
        '''
        try:
            values = self.grid.itervalues()
        except:
            values = self.grid.values()
        return values

    def potential_spawn_locations(self):
        '''
        :return: List of all possible spawn locations which do not hold an
        avatar or pickups.
        '''
        return (c for c in self.all_cells()
                if c.habitable
                and not c.avatar
                and not c.pickup)

    def pickup_cells(self):
        '''
        :return: List of possible spawn locations.
        '''
        return (c for c in self.all_cells() if c.pickup)

    def is_on_map(self, location):
        '''
        Checks whether the provided location exists in the grid.

        :param location: A location object, containing x and y.
        :return: A boolean true or false.
        '''
        try:
            self.grid[location]
        except KeyError:
            return False
        return True

    def get_cell(self, location):
        '''
        :param location: A location object containing x and y.
        :return: A single cell object at given location.
        '''
        try:
            return self.grid[location]
        except KeyError:
            raise ValueError('Location %s is not on the map' % location)

    def get_cell_by_coords(self, x, y):
        '''
        Helper function provided if no Location object is created for get_cell().
        :param x: Integer for x-coordinate.
        :param y: Integer for y-coordinate.
        :return: Cell object at location x,y.
        '''
        return self.get_cell(Location(x, y))

    # TODO: clear cell actions?????? Are we going to implement actions, or how else?

    def get_random_spawn_location(self):
        """Return a single random spawn location.

        Throws:
            IndexError: if there are no possible locations.
        """
        potential_locations = list(self.potential_spawn_locations())
        try:
            spawn_location = random.sample(potential_locations, 1)
            return spawn_location.location
        except ValueError:
            LOGGER.debug('Not enough potential locations!')
            return potential_locations[0].location

    def _get_random_spawn_locations(self, max_locations):
        if max_locations <= 0:
            return []
        potential_locations = list(self.potential_spawn_locations())
        try:
            return random.sample(potential_locations, max_locations)
        except ValueError:
            LOGGER.debug('Not enough potential locations')
            return potential_locations

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