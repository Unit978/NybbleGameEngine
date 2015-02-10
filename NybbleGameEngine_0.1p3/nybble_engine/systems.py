
from abc import abstractmethod

from components import *
from util_math import get_relative_rect_pos
from collections import deque

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

    tag = "physics system"

    top = 0
    bottom = 1
    left = 2
    right = 3

    gravity = Vector2(0.0, 500.0)

    # how much two colliders can overlap before resolution is applied
    collision_epsilon = 5

    # holds pairs of colliding entities per iteration.
    collision_queue = deque()

    def __init__(self):
        super(PhysicsSystem, self).__init__()

    def process(self, entities):

        # empty the collision queue
        PhysicsSystem.collision_queue.clear()

        for eA in entities:

            transform_a = eA.transform
            collider_a = eA.collider
            rigid_body_a = eA.rigid_body

            if collider_a is not None and rigid_body_a is not None:

                # Find another entity that it may collide with
                for eB in entities:

                    transform_b = eB.transform
                    collider_b = eB.collider
                    rigid_body_b = eB.rigid_body

                    # Check that coll_comp_b is valid and that coll_comp_a is not colliding with itself
                    if collider_b is not None and eA is not eB:

                        # Get the relative collision box positions to their transforms.
                        get_relative_rect_pos(transform_a.position, collider_a.box)
                        get_relative_rect_pos(transform_b.position, collider_b.box)

                        # check for collision
                        if collider_a.box.colliderect(collider_b.box):
                            PhysicsSystem.bounce(rigid_body_a, collider_a, rigid_body_b,  collider_b)

                            # add collision event into the queue
                            PhysicsSystem.collision_queue.append((eA, eB))

                            # call the collision inside the scripts
                            for s in eA.scripts:
                                s.collision_event(collider_b)

                            for s in eB.scripts:
                                s.collision_event(collider_a)

                # Move the rigid body
                self.move(transform_a, rigid_body_a)

    # Apply bouncing between two simplified rigid bodies. For right now,
    # rigid bodies are entities that do not rotate their collision polygons.
    # Basically, they are treated as particles
    # This should be called if there was a detected collision
    @staticmethod
    def bounce(rigid_a, collider_a, rigid_b, collider_b):

        # Obtain necessary components
        transform_a = collider_a.entity.get_component(Transform.tag)
        transform_b = collider_b.entity.get_component(Transform.tag)

        position_a = transform_a.position
        position_b = transform_b.position

        # Use the Minkowski sum of the two box colliders in
        # order to determine which sides of the boxes collide.
        # This is relative to coll_comp_a.

        width = 0.5 * (collider_a.box.width + collider_b.box.width)
        height = 0.5 * (collider_a.box.height + collider_b.box.height)

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

        # SUMMARY OF WHAT THE FOLLOWING CODE DOES

        # Invert velocities based on collision
        # Apply collision resolution to avoid colliders getting stuck with each other
        # Apply collision restitution...
        #   if A collided with B then apply B's restitution to A
        # Only bounce with a large enough velocity.

        rigid_a.velocity.x *= x_change * collider_b.restitution
        rigid_a.velocity.y *= y_change * collider_b.restitution

        # collision with rigid body
        if rigid_b is not None:
            rigid_b.velocity.x *= x_change * collider_a.restitution
            rigid_b.velocity.y *= y_change * collider_a.restitution

            PhysicsSystem.resolve_collision_with_rigid(orientation, transform_a, collider_a, transform_b, collider_b)

        # collision with another collider only
        else:
            PhysicsSystem.resolve_collision_with_collider(orientation, transform_a, collider_a, collider_b)

    # No acceleration implemented yet
    def move(self, transform, rigid_body):
        # time step
        dt = self.world.engine.delta_time

        # apply gravity
        if rigid_body.gravity_enabled:
            rigid_body.velocity += dt * rigid_body.gravity_scale * PhysicsSystem.gravity

        transform.position += dt * rigid_body.velocity

    @staticmethod
    def resolve_collision_with_rigid(orient, transform_a, collider_a, transform_b, collider_b):
        if orient == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = collider_b.box.bottom - collider_a.box.top

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

            # translate entity_b upwards
            transform_b.position.y -= delta

        elif orient == PhysicsSystem.bottom:
            delta = collider_a.box.bottom - collider_b.box.top

            # translate upwards
            transform_a.position.y -= delta
            transform_b.position.y += delta

        elif orient == PhysicsSystem.left:
            delta = collider_b.box.right - collider_a.box.left

            # translate to the right
            transform_a.position.x += delta
            transform_b.position.x -= delta

        elif orient == PhysicsSystem.right:
            delta = collider_a.box.right - collider_b.box.left

            # translate to the left
            transform_a.position.x -= delta
            transform_b.position.x += delta

    @staticmethod
    def resolve_collision_with_collider(orientation, transform_a, collider_a, collider_b):
        if orientation == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = collider_b.box.bottom - collider_a.box.top

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

        elif orientation == PhysicsSystem.bottom:
            delta = collider_a.box.bottom - collider_b.box.top

            #print(delta)

            # disable gravity if delta is very small
            #if abs(delta) < 2:
            #    collider_a.entity.rigid_body.gravity_enabled = False
            #else:
            #    collider_a.entity.rigid_body.gravity_enabled = True

            # translate upwards
            #if abs(delta) > PhysicsSystem.collision_epsilon:
            transform_a.position.y -= delta

        elif orientation == PhysicsSystem.left:
            delta = collider_b.box.right - collider_a.box.left

            # translate to the right
            transform_a.position.x += delta

        elif orientation == PhysicsSystem.right:
            delta = collider_a.box.right - collider_b.box.left

            # translate to the left
            transform_a.position.x -= delta


# Requires for an entity to have a render and transform component
# Holds the surface to render images
class RenderSystem (System):

    tag = "render system"

    def __init__(self):
        super(RenderSystem, self).__init__()

        # Dictionary of layers to simulate z-coordinate for
        # depth rendering.
        # Everything is added to the key '0' by default
        self.scene = dict()

        # default layer
        self.scene[0] = list()

        # Contains the layer enumerations in order from least to greatest
        self.ordered_layers = list()

        # Set up display for rendering.
        self.camera = None

    # This should be called once the initial entities have been made and right
    # before the main loop starts unless it is necessary to reconstruct a large
    # portions of entities in the scene.
    def construct_scene(self, entities):

        # clear the entire layer dictionary
        self.scene.clear()

        for e in entities:
            renderer = e.renderer
            if renderer is not None:

                depth = renderer.depth

                # the depth layer doesn't exist yet
                if not (depth in self.scene):

                    # create an empty list for that layer
                    self.scene[depth] = list()

                # add a renderer to that layer
                self.scene[depth].append(renderer)

        # create the layer order
        for key in self.scene:
            self.ordered_layers.append(key)

        # sort the layers
        self.ordered_layers.sort()

        # have the greater values be rendered first (z-coordinate simulation)
        self.ordered_layers.reverse()

    # Add a new entity to the scene.
    # Use this during the run time of the game
    def dynamic_insertion_to_scene(self, entity):
        renderer = entity.renderer
        if renderer is not None:
            depth = renderer.depth

            # layer already exists
            if depth in self.scene:
                self.scene[depth].append(renderer)

            # create new layer and re-sort
            else:
                self.scene[depth] = [renderer]

                # find where this new layers belongs in the layer order
                i = 0
                for layer in self.ordered_layers:

                    # found where to insert the depth
                    if layer > depth:
                        self.ordered_layers.insert(i, depth)
                        return
                    i += 1

                # the depth is the last layer
                self.ordered_layers.append(depth)

    # Use this to change the depth of an entity already in the scene.
    def update_depth(self, entity, new_depth):
        renderer = entity.renderer
        if renderer is not None:

            # save old depth and assign the new one
            old_depth = renderer.depth
            renderer.depth = new_depth

            # check that it exists in the scene
            if old_depth in self.scene:
                renderer_list = self.scene[old_depth]

                # find the renderer's entity
                i = 0
                for r in renderer_list:

                    # entity found - remove the renderer for that layer
                    if r.entity == renderer.entity:
                        renderer_list.pop(i)

                    i += 1

                # reinsert to the new layer
                self.dynamic_insertion_to_scene(entity)

            else:
                print("Renderer had not been added to the scene.")

    def remove_from_scene(self, entity):
        renderer = entity.renderer
        if renderer is not None:

            depth = renderer.depth

            # check that it exists in the scene
            if depth in self.scene:
                renderer_list = self.scene[depth]

                # find the renderer's entity
                i = 0
                for r in renderer_list:

                    # entity found - remove the renderer for that layer
                    if r.entity == renderer.entity:
                        renderer_list.pop(i)

                    i += 1

    def render_scene(self):

        # Iterate through each layer in the scene in order
        for layer in self.ordered_layers:

            renderer_list = self.scene[layer]

            for renderer in renderer_list:

                # access the transform
                entity = renderer.entity
                transform = entity.transform

                # transform exists
                if transform is not None:

                    # Center it around the image pivot
                    position = transform.position - renderer.pivot

                    # Offset image position with the camera
                    if self.camera is not None:
                        position -= self.camera.position

                    display = self.world.engine.display
                    display.blit(renderer.sprite, (position.x, position.y))

                else:
                    print("Renderer has no transform associated.")

    def process(self, entities):

        self.render_scene()

        for e in entities:

            # Obtain the proper components.
            transform = e.transform

            # Components found.
            if transform is not None:
                display = self.world.engine.display

                # ------- Debug info -------- #

                # draw collision box
                if self.world.engine.debug:
                    x = transform.position.x
                    y = transform.position.y

                    collider = e.collider
                    rigid_body = e.rigid_body

                    if rigid_body is not None:

                        # obtain a fraction of the velocity vector
                        length = Vector2.get_scaled_by(rigid_body.velocity, 0.2)
                        xend = x + length.x
                        yend = y + length.y

                        # draw the velocity vector of the rigid
                        pygame.draw.line(display, (0, 255, 0), (x, y), (xend, yend))

                    if collider is not None:
                        # get relative position to transform
                        get_relative_rect_pos(transform.position, collider.box)

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