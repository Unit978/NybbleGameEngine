from pygame import Rect
from abc import ABCMeta

from util_math import Vector2


# Base class for all components
class Component (object):

    __metaclass__ = ABCMeta

    def __init__(self):

        # The associated entity
        self.entity = None


# Basic transform that handles position , rotation and scale
class TransformComponent (Component):

    tag = "transform"

    def __init__(self, position=Vector2(0.0, 0.0), degrees=0, x_scale=1, y_scale=1):
        super(TransformComponent, self).__init__()
        self.position = position
        self.degrees = degrees
        self.scale = Vector2(x_scale, y_scale)


# Contains image to render
# pivot is of type Vector2 - it is the position relative to the image
# which specifies where to start drawing the image from.
# Rendering a image centered on a point would require that
# pivot = Vector2(image.width/2, image.height/2)

class RenderComponent (Component):
    tag = "render"

    def __init__(self, image, pivot=Vector2(0, 0)):
        super(RenderComponent, self).__init__()
        self.original_image = image
        self.sprite = image
        self.pivot = pivot


# Only holds velocity vector and mass scalar, may be expanded in future development
# for a better physics simulations
class RigidBodyComponent (Component):
    tag = "rigid body"

    def __init__(self, velocity=Vector2(0.0, 0.0), m=1.0):
        super(RigidBodyComponent, self).__init__()
        self.velocity = velocity
        self.mass = m


class CollisionBoxComponent (Component):
    tag = "collision box"

    def __init__(self, width=0.0, height=0.0):
        super(CollisionBoxComponent, self).__init__()
        self.box = Rect(0, 0, width, height)

    def set_box(self, width, height):
        self.box = Rect(0, 0, width, height)


# This component simply flags which entity can receive input.
class InputComponent (Component):
    tag = "input"

    def __init__(self):
        super(InputComponent, self).__init__()
        pass