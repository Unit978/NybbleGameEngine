
from managers import EntityManager
from entity import GameObject
from entity import BoxColliderGameObject
from systems import *


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

        # for world behavior
        self.scripts = list()

        # add the fundamental systems
        self.add_system(PhysicsSystem())
        self.add_system(RenderSystem())

    @abstractmethod
    def load_scene(self):
        """
        Setup the world scene by specifying how/where to create
        game objects.
        """

    # Do not override
    def _take_input(self, event):

        for s in self.scripts:
            s.take_input(event)

        # run script input
        for e in self.entity_manager.entities:
            e.take_input(event)

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

        # add to the front - so the physics and render systems are
        # the last systems to do their logic.
        self.systems.insert(0, system)

    def remove_system(self, system):
        self.systems.remove(system)

    def add_script(self, script):
        self.scripts.append(script)

    def remove_script(self, script):
        self.scripts.remove(script)

    # Have each system process the entities
    def run(self):
        for s in self.systems:
            s.process(self.entity_manager.entities)

        # run script updates
        for e in self.entity_manager.entities:
            if len(e.scripts) != 0:
                for s in e.scripts:
                    s.update()

        # world scripts
        for s in self.scripts:
            s.update()