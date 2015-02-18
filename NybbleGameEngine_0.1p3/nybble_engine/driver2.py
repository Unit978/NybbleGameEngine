
from world import *
from engine import *
from components import BehaviorScript

engine = Engine(1200, 700)


class CameraFollow(BehaviorScript):

    def __init__(self, script_name, target_transform, cam_width, cam_height):
        super(CameraFollow, self).__init__(script_name)
        self.target_transform = target_transform
        self.width = cam_width
        self.height = cam_height

    def update(self):

        # center the target transform in the middle of the camera
        x = self.target_transform.position.x - self.width/2
        y = self.target_transform.position.y - self.height/2

        renderer = self.target_transform.entity.renderer

        # center around the image attached to the target transform
        if renderer is not None:
            x += renderer.sprite.get_width()/2
            y += renderer.sprite.get_height()/2

        world = self.entity.world

        # keep camera within world bounds
        if world.is_bounded():
            if x < 0:
                x = 0

            elif x > world.width - self.width:
                x = world.width - self.width

            if y < 0:
                y = 0

            elif y > world.height - self.height:
                y = world.height - self.height

        self.entity.transform.position = Vector2(x, y)


# add movement to a platform but have it ignore physical properties
class PlatformMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlatformMovement, self).__init__(script_name)
        self.h_speed = 100
        self.velocity = Vector2(self.h_speed, 0)

    # implement custom movement without rigid
    def update(self):
        dt = self.entity.world.engine.delta_time
        transform = self.entity.transform
        transform.position += self.velocity * dt

    def collision_event(self, other_collider):

        # have the player go along with the platform
        if other_collider.entity.name == "player":
            other_collider.entity.rigid_body.velocity.x = self.velocity.x

            # apply friction sliding ???

        # make the platform bounce back and forth
        if other_collider.entity.tag == "side wall":
            self.velocity.x *= -1
            PhysicsSystem.box2box_response(self.entity.collider, other_collider)


class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.h_speed = 200
        self.v_speed = 300

    def update(self):

        keys = pygame.key.get_pressed()

        velocity = self.entity.rigid_body.velocity

        if keys[pygame.K_a]:
            velocity.x = -self.h_speed

        elif keys[pygame.K_d]:
            velocity.x = self.h_speed

    def take_input(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.entity.rigid_body.velocity.y = -self.v_speed


class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None
        self.background = None

        self.box = None

        self.platform = None
        self.floor = None

        # walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None

    def load_scene(self):

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()

        # world bounds
        self.width = w*2
        self.height = h

        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        # frames to demonstrate animation
        frame1 = pygame.Surface((50, 80)).convert()
        frame1.fill((255, 0, 0))

        frame2 = pygame.Surface((50, 80)).convert()
        frame2.fill((0, 255, 0))

        frame3 = pygame.Surface((50, 80)).convert()
        frame3.fill((0, 0, 255))

        frame4 = pygame.Surface((50, 80)).convert()
        frame4.fill((255, 255, 255))

        self.player = self.create_game_object(frame1)
        self.player.add_component(RigidBody())
        self.player.transform.position = Vector2(100, 100)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 2
        self.player.add_script(PlayerMovement("player_move"))
        self.player.collider.restitution = 0
        self.player.name = "player"

        # set up animation
        animation = Animator.Animation()

        # add frames to animation
        animation.add_frame(frame1)
        animation.add_frame(frame2)
        animation.add_frame(frame3)
        animation.add_frame(frame4)

        # set time between frames in seconds
        animation.frame_latency = 0.4

        # set the first animation
        animator = Animator()
        animator.current_animation = animation

        # add animator to player
        self.player.add_component(animator)

        platform_img = pygame.Surface((300, 100)).convert()
        platform_img.fill((150, 150, 150))
        self.platform = self.create_game_object(platform_img)
        self.platform.transform.position = Vector2(500, h - 350)
        self.platform.renderer.depth = -5
        self.platform.collider.restitution = 0
        self.platform.collider.surface_friction = 0.8
        self.platform.collider.treat_as_dynamic = True
        #self.platform.add_script(PlatformMovement("plat move"))

        box_img = pygame.Surface((60, 60)).convert()
        box_img.fill((200, 200, 200))

        self.box = self.create_game_object(box_img)
        self.box.transform.position = Vector2(400, 300)
        self.box.renderer.depth = -5
        self.box.collider.restitution = 0
        self.box.collider.surface_friction = 0.8

        self.box.add_component(RigidBody())
        self.box.rigid_body.velocity = Vector2(0.0, 0.0)
        self.box.rigid_body.gravity_scale = 2

        box2 = self.create_game_object(box_img)
        box2.transform.position = Vector2(400, 200)
        box2.renderer.depth = -5
        box2.collider.restitution = 0
        box2.collider.surface_friction = 0.8
        box2.add_component(RigidBody())
        box2.rigid_body.velocity = Vector2(0.0, 0.0)
        box2.rigid_body.gravity_scale = 2

        box3 = self.create_game_object(box_img)
        box3.transform.position = Vector2(400, 100)
        box3.renderer.depth = -5
        box3.collider.restitution = 0
        box3.collider.surface_friction = 0.8

        box3.add_component(RigidBody())
        box3.rigid_body.velocity = Vector2(0.0, 0.0)
        box3.rigid_body.gravity_scale = 2

        floor_image = pygame.Surface((w*2, 200)).convert()
        floor_image.fill((50, 50, 50))

        self.floor = self.create_game_object(floor_image)
        self.floor.transform.position = Vector2(w, h-100)
        self.floor.collider.restitution = 0
        self.floor.collider.surface_friction = 0.8

        # Create the wall entities and set their collision boxes.
        # Make these wall thick, so the ball doesn't escape from the level.
        self.topWall = self.create_box_collider_object(w*2, 200)
        self.leftWall = self.create_box_collider_object(200, h*2)
        #self.rightWall = self.create_box_collider_object(200, h*2)

        # set up wall positions
        self.topWall.transform.position = Vector2(w/2, 0-100)
        self.leftWall.transform.position = Vector2(0, h/2-50)
        #self.rightWall.transform.position = Vector2(w, h/2+50)

        self.leftWall.tag = "side wall"
        #self.rightWall.tag = "side wall"

        render = self.get_system(RenderSystem.tag)

        render.camera = self.create_entity()
        render.camera.add_component(Transform(Vector2(0, 0)))
        render.camera.add_script(CameraFollow("cam follow", self.player.transform, w, h))

        #PhysicsSystem.gravity.zero()

engine.set_world(PlatformWorld())
engine.run()
