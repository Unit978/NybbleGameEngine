from abc import abstractmethod
from abc import ABCMeta

from nybble_engine.managers import EntityManager
from nybble_engine.entity import GameObject
from nybble_engine.entity import BoxColliderGameObject


# A world is like a game level. It holds the necessary game objects
# and assets to be used for a level.
# Inherit from this class and implement the abstract methods in order
# to create a custom world.

class World (object):
    __metaclass__ = ABCMeta

    def __init__(self, engine=None):
        # Reference to the engine that it exists in
        self.engine = engine
        self.systems = list()
        self.entity_manager = EntityManager()

    @abstractmethod
    def load_scene(self):
        """
        Setup the world scene by specifying how/where to create
        game objects.
        """

    @abstractmethod
    def take_input(self, event):
        """
        Takes in user input from a peripheral input device
        such as the mouse or the keyboard.
        """

    def create_entity(self):
        return self.entity_manager.create_entity()

    def create_game_object(self, image_surface):
        entity = GameObject(image_surface)
        self.entity_manager.add(entity)
        return entity

    def create_box_collider_game_object(self, width, height):
        entity = BoxColliderGameObject(width, height)
        self.entity_manager.add(entity)
        return entity

    def destroy_entity(self, entity):
        self.entity_manager.remove_entity(entity)

    def add_system(self, system):
        system.world = self
        self.systems.append(system)

    def remove_system(self, system):
        self.systems.remove(system)

    # Have each system process the entities
    def run(self):
        for s in self.systems:
            s.process(self.entity_manager.entities)