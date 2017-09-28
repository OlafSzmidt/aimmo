from __future__ import absolute_import

import math
from string import ascii_uppercase

from unittest import TestCase

from simulation.geography.location import Location
from simulation.world_map import WorldMap, world_map_static_spawn_decorator
from simulation.geography.cell import Cell
from .dummy_avatar import DummyAvatar
from .maps import MockCell, MockPickup


def int_ceil(num):
    return int(math.ceil(num))


def int_floor(num):
    return int(math.floor(num))


class Serialiser(object):
    def __init__(self, content):
        self.content = content

    def serialise(self):
        return self.content


class TestCell(TestCase):
    def test_equal(self):
        cell1 = Cell(1)
        cell2 = Cell(1)
        self.assertEqual(cell1, cell2)

    def test_not_equal(self):
        cell1 = Cell(1)
        cell2 = Cell(2)
        self.assertNotEqual(cell1, cell2)

    def _create_full_cell(self):
        cell = Cell(Serialiser('location'), False, True)
        cell.avatar = Serialiser('avatar')
        cell.pickup = Serialiser('pickup')
        self.expected = {
            'avatar': 'avatar',
            'habitable': False,
            'location': 'location',
            'pickup': 'pickup',
        }
        return cell

    def test_serialise(self):
        cell = self._create_full_cell()
        self.assertEqual(cell.serialise(), self.expected)

    def test_serialise_no_avatar(self):
        cell = self._create_full_cell()
        cell.avatar = None
        self.expected['avatar'] = None
        self.assertEqual(cell.serialise(), self.expected)

    def test_serialise_no_pickup(self):
        cell = self._create_full_cell()
        cell.pickup = None
        self.expected['pickup'] = None
        self.assertEqual(cell.serialise(), self.expected)


class TestWorldMap(TestCase):
    def setUp(self):
        self.settings = {
            'TARGET_NUM_CELLS_PER_AVATAR': 0,
            'TARGET_NUM_PICKUPS_PER_AVATAR': 0,
            'TARGET_NUM_SCORE_LOCATIONS_PER_AVATAR': 0,
            'SCORE_DESPAWN_CHANCE': 0,
            'PICKUP_SPAWN_CHANCE': 0,
        }

    def _generate_grid(self, columns=2, rows=2):
        alphabet = iter(ascii_uppercase)
        grid = {Location(x, y): MockCell(Location(x, y), name=next(alphabet))
                for x in range(columns) for y in range(rows)}
        return grid

    def _grid_from_list(self, in_list):
        out = {}
        for x, column in enumerate(in_list):
            for y, cell in enumerate(column):
                out[Location(x, y)] = cell
        return out

    def assertGridSize(self, map, expected_columns, expected_rows=None):
        if expected_rows is None:
            expected_rows = expected_columns
        self.assertEqual(map.num_rows, expected_rows)
        self.assertEqual(map.num_cols, expected_columns)
        self.assertEqual(map.num_cells, expected_rows*expected_columns)
        self.assertEqual(len(list(map.all_cells())), expected_rows*expected_columns)

    def test_grid_size(self):
        map = WorldMap(self._generate_grid(1, 3), self.settings)
        self.assertGridSize(map, 1, 3)

    def test_generated_map(self):
        map = WorldMap.generate_empty_map(2, 5, {})
        self.assertGridSize(map, 5, 2)

    def test_all_cells(self):
        map = WorldMap(self._generate_grid(), self.settings)
        cell_names = [c.name for c in map.all_cells()]
        self.assertIn('A', cell_names)
        self.assertIn('B', cell_names)
        self.assertIn('C', cell_names)
        self.assertIn('D', cell_names)
        self.assertEqual(len(cell_names), 4)

    def test_potential_spawns(self):
        spawnable1 = MockCell()
        spawnable2 = MockCell()
        unhabitable = MockCell(habitable=False)
        filled = MockCell(avatar='avatar')
        grid = self._grid_from_list([[spawnable1, unhabitable], [unhabitable, spawnable2, filled]])
        map = WorldMap(grid, self.settings)
        cells = list(map.potential_spawn_locations())
        self.assertIn(spawnable1, cells)
        self.assertIn(spawnable2, cells)
        self.assertNotIn(unhabitable, cells, "Unhabitable cells should not be spawns")
        self.assertNotIn(filled, cells, "Cells with avatars should not be spawns")
        self.assertEqual(len(cells), 2)

    def test_pickup_cells(self):
        pickup_cell1 = MockCell(pickup=MockPickup())
        pickup_cell2 = MockCell(pickup=MockPickup())
        no_pickup_cell = MockCell()
        grid = self._grid_from_list([[pickup_cell1, no_pickup_cell], [no_pickup_cell, pickup_cell2]])
        map = WorldMap(grid, self.settings)
        cells = list(map.pickup_cells())
        self.assertIn(pickup_cell1, cells)
        self.assertIn(pickup_cell2, cells)
        self.assertEqual(len(cells), 2, "Non-pickup cells present")

    def test_location_on_map(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for x in (0, 1):
            for y in (0, 1):
                self.assertTrue(map.is_on_map(Location(x, y)))

    def test_x_off_map(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for y in (0, 1):
            self.assertFalse(map.is_on_map(Location(-1, y)))
            self.assertFalse(map.is_on_map(Location(2, y)))

    def test_y_off_map(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for x in (0, 1):
            self.assertFalse(map.is_on_map(Location(x, -1)))
            self.assertFalse(map.is_on_map(Location(x, 2)))

    def test_get_valid_cell(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for x in (0, 1):
            for y in (0, 1):
                location = Location(x, y)
                self.assertEqual(map.get_cell(location).location, location)

    def test_get_x_off_map(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for y in (0, 1):
            with self.assertRaises(ValueError):
                map.get_cell(Location(-1, y))
            with self.assertRaises(ValueError):
                map.get_cell(Location(2, y))

    def test_get_y_off_map(self):
        map = WorldMap(self._generate_grid(), self.settings)
        for x in (0, 1):
            with self.assertRaises(ValueError):
                map.get_cell(Location(x, -1))
            with self.assertRaises(ValueError):
                map.get_cell(Location(x, 2))

    def test_grid_expand(self):
        self.settings['TARGET_NUM_CELLS_PER_AVATAR'] = 5
        map = WorldMap(self._generate_grid(), self.settings)
        map.update(1)
        self.assertTrue(map.is_on_map(Location(-1, -1)))
        self.assertTrue(map.is_on_map(Location(-1, 2)))
        self.assertTrue(map.is_on_map(Location(2, 2)))
        self.assertTrue(map.is_on_map(Location(2, -1)))
        self.assertGridSize(map, 4)
        map.update(4)
        self.assertGridSize(map, 6)
        self.assertTrue(map.is_on_map(Location(0, 3)))
        self.assertTrue(map.is_on_map(Location(3, 0)))
        self.assertTrue(map.is_on_map(Location(-2, 0)))
        self.assertTrue(map.is_on_map(Location(0, -2)))

    def test_grid_doesnt_expand(self):
        self.settings['TARGET_NUM_CELLS_PER_AVATAR'] = 4
        map = WorldMap(self._generate_grid(), self.settings)
        map.update(1)
        self.assertGridSize(map, 2)

    def test_pickups_added(self):
        self.settings['TARGET_NUM_PICKUPS_PER_AVATAR'] = 1
        self.settings['PICKUP_SPAWN_CHANCE'] = 1
        map = WorldMap(self._generate_grid(), self.settings)
        map.update(1)
        self.assertEqual(len(list(map.pickup_cells())), 1)

        map.update(2)
        self.assertEqual(len(list(map.pickup_cells())), 2)

    def test_pickups_applied(self):
        grid = self._generate_grid()
        pickup = MockPickup()
        avatar = DummyAvatar()
        grid[Location(1, 1)].pickup = pickup
        grid[Location(1, 1)].avatar = avatar
        WorldMap(grid, self.settings).update(1)
        self.assertEqual(pickup.applied_to, avatar)

    def test_pickup_spawn_chance(self):
        self.settings['TARGET_NUM_PICKUPS_PER_AVATAR'] = 5
        self.settings['PICKUP_SPAWN_CHANCE'] = 0
        grid = self._generate_grid()
        map = WorldMap(grid, self.settings)
        map.update(1)
        self.assertEqual(len(list(map.pickup_cells())), 0)

    def test_pickups_not_added_when_at_target(self):
        self.settings['TARGET_NUM_PICKUPS_PER_AVATAR'] = 1
        grid = self._generate_grid()
        grid[Location(0, 1)].pickup = MockPickup()
        map = WorldMap(grid, self.settings)
        map.update(1)
        self.assertEqual(len(list(map.pickup_cells())), 1)
        self.assertIn(grid[Location(0, 1)], map.pickup_cells())

    def test_not_enough_pickup_space(self):
        self.settings['TARGET_NUM_PICKUPS_PER_AVATAR'] = 1
        grid = self._generate_grid(1, 1)
        grid[Location(0, 0)].generates_score = True
        map = WorldMap(grid, self.settings)
        map.update(1)
        self.assertEqual(len(list(map.pickup_cells())), 0)

    def test_random_spawn_location(self):
        cell = MockCell()
        map = WorldMap({Location(0, 0): cell}, self.settings)
        self.assertEqual(map.get_random_spawn_location(), cell.location)

    def test_random_spawn_location_with_no_candidates(self):
        grid = self._generate_grid(1, 1)
        map = WorldMap(grid, self.settings)
        grid[Location(0, 0)].avatar = True
        with self.assertRaises(IndexError):
            map.get_random_spawn_location()

    def test_can_move_to(self):
        map = WorldMap(self._generate_grid(), self.settings)
        target = Location(1, 1)
        self.assertTrue(map.can_move_to(target))

    def test_cannot_move_to_cell_off_grid(self):
        map = WorldMap(self._generate_grid(), self.settings)
        target = Location(4, 1)
        self.assertFalse(map.can_move_to(target))

    def test_cannot_move_to_uninhabitable_cell(self):
        target = Location(0, 0)
        cell = MockCell(target, habitable=False)
        map = WorldMap({target: cell}, self.settings)
        self.assertFalse(map.can_move_to(target))

    def test_cannot_move_to_habited_cell(self):
        target = Location(0, 0)
        cell = MockCell(target, avatar=DummyAvatar(target, 0))
        map = WorldMap({target: cell}, self.settings)
        target = Location(0, 0)
        self.assertFalse(map.can_move_to(target))

    def test_empty_grid(self):
        map = WorldMap({}, self.settings)
        self.assertFalse(map.is_on_map(Location(0, 0)))

    def test_iter(self):
        grid = [
            [MockCell(Location(-1, -1), name='A'), MockCell(Location(-1, 0), name='B'), MockCell(Location(-1, 1), name='C')],
            [MockCell(Location(0, -1), name='D'), MockCell(Location(0, 0), name='E'), MockCell(Location(0, 1), name='F')],
            [MockCell(Location(1, -1), name='E'), MockCell(Location(1, 0), name='G'), MockCell(Location(1, 1), name='H')],
        ]
        map = WorldMap(self._grid_from_list(grid), self.settings)
        self.assertEqual([list(column) for column in map], grid)


class TestWorldMapWithOriginCentre(TestWorldMap):
    def _generate_grid(self, columns=2, rows=2):
        alphabet = iter(ascii_uppercase)
        grid = {Location(x, y): MockCell(Location(x, y), name=next(alphabet))
                for x in range(-int_ceil(columns/2.0)+1, int_floor(columns/2.0)+1) for y in range(-int_ceil(rows/2.0)+1, int_floor(rows/2.0)+1)}

        return grid

    def _grid_from_list(self, in_list):
        out = {}
        min_x = -int_ceil(len(in_list)/2.0) + 1
        min_y = -int_ceil(len(in_list[0])/2.0) + 1
        for i, column in enumerate(in_list):
            x = i + min_x
            for j, cell in enumerate(column):
                y = j + min_y
                out[Location(x, y)] = cell
        return out

    def test_retrieve_negative(self):
        map = WorldMap(self._generate_grid(3, 3), self.settings)
        self.assertTrue(map.is_on_map(Location(-1, -1)))


class TestStaticSpawnDecorator(TestCase):
    def test_spawn_is_static(self):
        decorated_map = world_map_static_spawn_decorator(WorldMap({}, {}), Location(3, 7))
        for _ in range(5):
            self.assertEqual(decorated_map.get_random_spawn_location(), Location(3, 7))
