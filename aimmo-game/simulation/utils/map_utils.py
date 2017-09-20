import math
import random
from logging import getLogger

from simulation.expansion_layers import ExpansionLayers
from simulation.pickups import ALL_PICKUPS
from simulation.world_state import MapFeature

LOGGER = getLogger(__name__)


class UpdateMapAndAvatars(object):

    world_map = None

    def update_avatars_and_map(self, world_map, no_of_avatars):
        """
        Update the world avatars and the map with the
        number of avatars.
        """
        self.world_map = world_map
        self._update_avatars()
        self._update_map(no_of_avatars)

    def _update_avatars(self):
        """
        Apply the score and pickups to the avatars.
        """
        self._apply_score()
        self._apply_pickups()

    def _apply_score(self):
        """
        Increase the avatar score for every cell that generates score.

        Throws:
            AttributeError: If the avatar could not be resolved (check?)
        """
        for cell in self.world_map.score_cells():
            try:
                cell.avatar.score += 1
            except AttributeError:
                pass

    def _apply_pickups(self):
        """
        Similar to above. If avatar exists, and the cell is a pickup cell
        then apply the pickup.

        Throws:
            AttributeError: If the avatar could not be resolved (check?)
        """
        for cell in self.world_map.pickup_cells():
            try:
                cell.pickup.apply(cell.avatar)
            except AttributeError:
                pass

    def _update_map(self, no_of_avatars):
        """
        * Expand the map for the number of avatars.
        * Generate new score spawns.
        * Add new pickups to compensate for more avatars.
        """
        self._expand(no_of_avatars)
        self._reset_score_locations(no_of_avatars)
        self._add_pickups(no_of_avatars)

    def _expand(self, no_of_avatars):
        """
        Calculates the new target size of the map and adds it. It
        ensures the number can only increase, not decrease.

        Throws:
            AssertionError: if the final number of cells is less than the start
                            size.
        """
        start_no_of_cells = self.world_map.num_cells
        target_no_of_cells = int(math.ceil(no_of_avatars
                                           * self.world_map.settings['TARGET_NUM_CELLS_PER_AVATAR']))
        no_of_cells_to_add = target_no_of_cells - self.world_map.num_cells
        if no_of_cells_to_add > 0:
            ExpansionLayers.add_outer_layer(self.world_map)
            assert self.world_map.num_cells > start_no_of_cells

    def _reset_score_locations(self, no_of_avatars):
        """
        Based on SCORE_DESPAWN_CHANCE, remove random score points from the scene.
        Then generate new random ones to meet the target score point locations.
        """
        for cell in self.world_map.score_cells():
            if random.random() < self.world_map.settings['SCORE_DESPAWN_CHANCE']:
                # Remove the score point from the scene if there was one.
                if cell.generates_score:
                    cell.remove_from_scene = MapFeature.SCORE_POINT
                cell.generates_score = False

        new_no_of_score_locations = len(list(self.world_map.score_cells()))
        target_no_of_score_locations = int(math.ceil(
            no_of_avatars * self.world_map.settings['TARGET_NUM_SCORE_LOCATIONS_PER_AVATAR']
        ))

        no_of_score_locations_to_add = target_no_of_score_locations - new_no_of_score_locations
        locations = self._get_random_spawn_locations(no_of_score_locations_to_add)
        for cell in locations:
            # Add the score point to the scene if there wasn't one.
            if not cell.generates_score:
                cell.add_to_scene = MapFeature.SCORE_POINT
            cell.generates_score = True

    def _get_random_spawn_locations(self, max_locations):
        """
        A private utility that has the same logic as get_random_spawn_locations_external
        but can only be called from this class for this instance of world_map.

        Throws:
            ValueError: if there are not enough potential locations provided.
        """
        # We account for a scenario where the target number of score locations
        # is equal to the score locations that already exist.
        if max_locations <= 0:
            return []
        potential_locations = list(self.world_map.potential_spawn_locations())
        try:
            return random.sample(potential_locations, max_locations)
        except ValueError:
            LOGGER.debug('Not enough potential locations')
            return potential_locations

    @classmethod
    def get_random_spawn_locations_external(cls, world_map, max_locations):
        """
        A class utility that is uses the same functionality as above but
        allows to be called from anywhere for any map (for the purpose of
        world_map design).

        Throws:
            ValueError: if there are not enough potential locations provided.
        """
        # We account for a scenario where the target number of score locations
        # is equal to the score locations that already exist.
        if max_locations <= 0:
            return []
        potential_locations = list(world_map.potential_spawn_locations())
        try:
            return random.sample(potential_locations, max_locations)
        except ValueError:
            LOGGER.debug('Not enough potential locations')
            return potential_locations

    def _add_pickups(self, no_of_avatars):
        """
        * Calculates the target number of pickups based on the amount of avatars.
        * Makes sure the max added number of pickups = target - already existing pickups
        * Finds random locations and spawns it based on PICKUP_SPAWN_CHANCE.
        """
        target_no_of_pickups = int(math.ceil(no_of_avatars *
                                             self.world_map.settings['TARGET_NUM_PICKUPS_PER_AVATAR']))

        LOGGER.debug('Aiming for %s new pickups', target_no_of_pickups)
        max_no_of_pickups_to_add = target_no_of_pickups - len(list(self.world_map.pickup_cells()))
        locations = self._get_random_spawn_locations(max_no_of_pickups_to_add)
        for cell in locations:
            if random.random() < self.world_map.settings['PICKUP_SPAWN_CHANCE']:
                LOGGER.info('Adding new pickup at %s', cell)
                # ALL_PICKUPS consists of: HealthPickup, InvulnerabilityPickup
                # and DamagePickup.
                cell.pickup = random.choice(ALL_PICKUPS)(cell)

