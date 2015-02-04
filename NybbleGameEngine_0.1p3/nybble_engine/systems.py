
from abc import abstractmethod

from nybble_engine.components import *
from nybble_engine.util_math import get_relative_rect_pos

import pygame


class System (object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # A reference to the world this system is operating in.
        self.world = None

    @abstractmethod
    def process(self, entities):
        """
        This is where the behavior of the system is implemented.
        """


# Detects collision between objects with Collision Box Components
# Handles basic bouncing collision between objects.

class PhysicsSystem (System):

    __metaclass__ = ABCMeta

    top = 0
    bottom = 1
    left = 2
    right = 3

    def __init__(self):
        super(PhysicsSystem, self).__init__()

    def process(self, entities):
        for eA in entities:

            transform_a = eA.get_component(TransformComponent.tag)
            coll_comp_a = eA.get_component(CollisionBoxComponent.tag)
            rigid_body_a = eA.get_component(RigidBodyComponent.tag)

            if coll_comp_a is not None and rigid_body_a is not None:

                # Find another entity that it may collide with
                for eB in entities:

                    transform_b = eB.get_component(TransformComponent.tag)
                    coll_comp_b = eB.get_component(CollisionBoxComponent.tag)
                    rigid_body_b = eB.get_component(RigidBodyComponent.tag)

                    # Check that coll_comp_b is valid and that coll_comp_a is not colliding with itself
                    if coll_comp_b is not None and eA is not eB:

                        # Get the relative collision box positions to their transforms.
                        get_relative_rect_pos(transform_a.position, coll_comp_a.box)
                        get_relative_rect_pos(transform_b.position, coll_comp_b.box)

                        # check for collision
                        if coll_comp_a.box.colliderect(coll_comp_b.box):
                            PhysicsSystem.bounce(rigid_body_a, coll_comp_a, rigid_body_b,  coll_comp_b)
                            self.collision_event(eA, eB)

                # Move the rigid body
                self.move(transform_a, rigid_body_a)

    # Apply bouncing between two simplified rigid bodies. For right now,
    # rigid bodies are entities that do not rotate their collision polygons.
    # Basically, they are treated as particles
    # This should be called if there was a detected collision
    @staticmethod
    def bounce(rigid_a, coll_comp_a, rigid_b, coll_comp_b):

        # Obtain necessary components
        transform_a = coll_comp_a.entity.get_component(TransformComponent.tag)
        transform_b = coll_comp_b.entity.get_component(TransformComponent.tag)

        position_a = transform_a.position
        position_b = transform_b.position

        # Use the Minkowski sum of the two box colliders in
        # order to determine which sides of the boxes collide.
        # This is relative to coll_comp_a.

        width = 0.5 * (coll_comp_a.box.width + coll_comp_b.box.width)
        height = 0.5 * (coll_comp_a.box.height + coll_comp_b.box.height)

        # Pay close attention to the operands
        dx = position_b.x - position_a.x
        dy = position_a.y - position_b.y

        # changes the velocity vector
        x_change = 1
        y_change = 1

        # Another way to detect collision
        # if abs(dx) <= width and abs(dy) <= height:

        wy = width * dy
        hx = height * dx

        # ------- determine where it hit ------- #
        if wy > hx:

            # collision from the top
            if wy > -hx:
                y_change = -1
                orientation = PhysicsSystem.top

            # collision from the left
            # wy <= -hx
            else:
                x_change = -1
                orientation = PhysicsSystem.left

        # wy <= hx
        else:
            # collision from the right
            if wy > -hx:
                x_change = -1
                orientation = PhysicsSystem.right

            # collision from the bottom
            # wy <= -hx
            else:
                y_change = -1
                orientation = PhysicsSystem.bottom

        # invert velocities based on collision
        # apply collision resolution to avoid colliders getting stuck with each other

        rigid_a.velocity.x *= x_change
        rigid_a.velocity.y *= y_change

        # collision with rigid body
        if rigid_b is not None:
            rigid_b.velocity.x *= x_change
            rigid_b.velocity.y *= y_change

            PhysicsSystem.resolve_collision_with_rigid(orientation, transform_a, coll_comp_a, transform_b, coll_comp_b)

        # collision with another collider only
        else:
            PhysicsSystem.resolve_collision_with_collider(orientation, transform_a, coll_comp_a, coll_comp_b)

    # No acceleration implemented yet
    def move(self, transform, rigid_body):
        # time step
        dt = self.world.engine.delta_time

        transform.position += dt * rigid_body.velocity

    @staticmethod
    def resolve_collision_with_rigid(orient, transform_a, coll_a, transform_b, coll_b):
        if orient == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = coll_b.box.bottom - coll_a.box.top

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

            # translate entity_b upwards
            transform_b.position.y -= delta

        elif orient == PhysicsSystem.bottom:
            delta = coll_a.box.bottom - coll_b.box.top

            # translate upwards
            transform_a.position.y -= delta
            transform_b.position.y += delta

        elif orient == PhysicsSystem.left:
            delta = coll_b.box.right - coll_a.box.left

            # translate to the right
            transform_a.position.x += delta
            transform_b.position.x -= delta

        elif orient == PhysicsSystem.right:
            delta = coll_a.box.right - coll_b.box.left

            # translate to the left
            transform_a.position.x -= delta
            transform_b.position.x += delta

    @staticmethod
    def resolve_collision_with_collider(orientation, transform_a, coll_comp_a, coll_comp_b):
        if orientation == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = coll_comp_b.box.bottom - coll_comp_a.box.top

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

        elif orientation == PhysicsSystem.bottom:
            delta = coll_comp_a.box.bottom - coll_comp_b.box.top

            # translate upwards
            transform_a.position.y -= delta

        elif orientation == PhysicsSystem.left:
            delta = coll_comp_b.box.right - coll_comp_a.box.left

            # translate to the right
            transform_a.position.x += delta

        elif orientation == PhysicsSystem.right:
            delta = coll_comp_a.box.right - coll_comp_b.box.left

            # translate to the left
            transform_a.position.x -= delta

    # Implement behavior of what should occur if two objects collide.
    # For example, if a bullet collides with an enemy then destroy the bullet
    # and decrease health from the enemy.
    def collision_event(self, entity_a, entity_b):
        pass


# Requires for an entity to have a render and transform component
# Holds the surface to render images
class RenderSystem (System):
    def __init__(self):
        super(RenderSystem, self).__init__()

        # Set up display for rendering.
        self.camera = None

    def process(self, entities):
        for e in entities:

            # Obtain the proper components.
            render_comp = e.get_component(RenderComponent.tag)
            transform_comp = e.get_component(TransformComponent.tag)

            # Components found.
            if transform_comp is not None:
                if render_comp is not None:

                    # Center it around the image pivot
                    position = transform_comp.position - render_comp.pivot

                    # Offset image position with the camera
                    if self.camera is not None:
                        position -= self.camera.position

                    display = self.world.engine.display
                    display.blit(render_comp.sprite, (position.x, position.y))

                # ------- Debug info -------- #

                # draw collision box
                if self.world.engine.debug:
                    x = transform_comp.position.x
                    y = transform_comp.position.y

                    collider = e.get_component(CollisionBoxComponent.tag)
                    rigid_body = e.get_component(RigidBodyComponent.tag)

                    if rigid_body is not None:

                        # obtain a fraction of the velocity vector
                        length = Vector2.get_scaled_by(rigid_body.velocity, 0.2)
                        xend = x + length.x
                        yend = y + length.y

                        # draw the velocity vector of the rigid
                        pygame.draw.line(display, (0, 255, 0), (x, y), (xend, yend))

                    if collider is not None:
                        # get relative position to transform
                        get_relative_rect_pos(transform_comp.position, collider.box)

                        display = self.world.engine.display

                        # display collider rect properties
                        pygame.draw.rect(display, (255, 255, 255), collider.box, 1)
                        pygame.draw.circle(display, (0, 255, 0), collider.box.center, 5)
                        pygame.draw.circle(display, (0, 255, 255), collider.box.topleft, 5)

                    # transform origin crosshair
                    pygame.draw.line(display, (255, 0, 0), (x-50, y), (x+50, y))
                    pygame.draw.line(display, (255, 0, 0), (x, y-50), (x, y+50))

                    # draw position vector
                    pygame.draw.line(display, (50, 50, 50), (0, 0), (x, y))