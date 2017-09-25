import math

from simulation.maps.world_maps import WorldMaps
from simulation.location import Location
from simulation.maps.cell import Cell

# REMOVED MANY SETTINGS HERE. CHECK.
DEFAULT_LEVEL_SETTINGS = {
    'TARGET_NUM_CELLS_PER_AVATAR': 0,
    'TARGET_NUM_PICKUPS_PER_AVATAR': 0,
    'PICKUP_SPAWN_CHANCE': 0,
}


class GenerateEmptyMap:

    @classmethod
    def generate_empty_map(cls, height, width, settings):
        '''
        Generate a new map based on the default settings.
        :param height: of the map on the y-coordinate system.
        :param width: of the map on the x-coordinate system.
        :param settings: dictionary with any fields that need to be changed from default.
        :return: a WorldMaps object.
        '''
        new_settings = DEFAULT_LEVEL_SETTINGS.copy()
        new_settings.update(settings)

        (min_x, max_x, min_y, max_y) = GenerateEmptyMap._min_max_from_dimensions(height, width)
        grid = {}
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                location = Location(x, y)
                grid[location] = Cell(location)
        return WorldMaps(grid, new_settings)

    @classmethod
    def _min_max_from_dimensions(cls, height, width):
        '''
        A private helper function that calculates minimum x,y and
        maximum x,y params.
        :param height: of the map on the y-coordinate system.
        :param width: of the map on the x-coordinate system.
        :return: 4 ints with the minimum and maximum coords.
        '''
        max_x = int(math.floor(width / 2))
        min_x = -(width - max_x - 1)
        max_y = int(math.floor(height / 2))
        min_y = -(height - max_y - 1)
        return min_x, max_x, min_y, max_y
