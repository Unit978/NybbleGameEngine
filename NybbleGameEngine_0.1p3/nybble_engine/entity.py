import components
from util_math import Vector2


class Entity (object):

    # Unique id should be modified by the entity manager
    def __init__(self, uuid=0):
        self.uuid = uuid
        self.components = list()
        self.tag = ""

    def add_component(self, component):
        component.entity = self
        self.components.append(component)

    def remove_component(self, component):
        self.components.remove(component)

    def get_component(self, component_tag):
        for c in self.components:
            if c.tag == component_tag:
                return c
        return None

    def __eq__(self, other):
        return self.uuid == other.uuid


# A basic game object with a transform, render, box collision, and rigid body components.
# The image is centered for the render component.
# In order to create a game object, the initial sprite image must be specified.
class GameObject (Entity):
    def __init__(self, image_surface, uuid=0):
        super(GameObject, self).__init__(uuid)

        # Set up pivot for the image
        pivot = Vector2(image_surface.get_width()/2, image_surface.get_height()/2)

        self.add_component(components.TransformComponent())
        self.add_component(components.RenderComponent(image_surface, pivot))
        self.add_component(components.CollisionBoxComponent())


# A game object with only a transform and collision box components.
# Could be used to create invisible game barriers
class BoxColliderGameObject (Entity):
    def __init__(self, width, height, uuid=0):
        super(BoxColliderGameObject, self).__init__(uuid)

        self.add_component(components.TransformComponent())
        self.add_component(components.CollisionBoxComponent(width, height))