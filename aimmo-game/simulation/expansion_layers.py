from simulation.world_map import Cell
from simulation.location import Location


class ExpansionLayers(object):
    """
    A utility class provided for all the layer logic moved
    from world_map and places in game_state. The only
    accessible method should be add_outer_layer by other classes.
    """

    @classmethod
    def add_outer_layer(cls, world_map):
        """
        * Expand the map for the number of avatars.
        * Generate new score spawns.
        * Add new pickups to compensate for more avatars.
        """
        cls._add_vertical_layer(world_map, world_map.min_x() - 1)
        cls._add_vertical_layer(world_map, world_map.max_x() + 1)
        cls._add_horizontal_layer(world_map, world_map.min_y() - 1)
        cls._add_horizontal_layer(world_map, world_map.max_y() + 1)

    @classmethod
    def _add_vertical_layer(cls, world_map, x):
        for y in range(world_map.min_y(), world_map.max_y() + 1):
            world_map.grid[Location(x, y)] = Cell(Location(x, y))

    @classmethod
    def _add_horizontal_layer(cls, world_map, y):
        for x in range(world_map.min_x(), world_map.max_x() + 1):
            world_map.grid[Location(x, y)] = Cell(Location(x, y))
