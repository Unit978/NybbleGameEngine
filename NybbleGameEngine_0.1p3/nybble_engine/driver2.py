
from world import *
from engine import *
from components import BehaviorScript

engine = Engine(1200, 700)


class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.h_speed = 200
        self.v_speed = 300

    def update(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.entity.rigid_body.velocity.x = -self.h_speed

        elif keys[pygame.K_d]:
            self.entity.rigid_body.velocity.x = self.h_speed

    def take_input(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.entity.rigid_body.velocity.y = -self.v_speed


class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None
        self.background = None

        self.ball1 = None
        self.ball2 = None

        self.box = None
        self.floor = None

        # walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None

    def load_scene(self):

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()
        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        player_image = pygame.Surface((50, 80)).convert()
        player_image.fill((255, 0, 0))

        self.player = self.create_game_object(player_image)
        self.player.add_component(RigidBody())
        self.player.transform.position = Vector2(100, 100)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 1
        self.player.add_script(PlayerMovement("player_move"))
        self.player.collider.restitution = 0.1

        self.ball1 = self.create_circle_collider_object(80)
        self.ball1.add_component(RigidBody())
        self.ball1.transform.position = Vector2(10, 300)
        self.ball1.rigid_body.velocity = Vector2(300, 0)
        self.ball1.rigid_body.mass = 20
        self.ball1.rigid_body.gravity_scale = 1
        self.ball1.collider.restitution = 1

        self.ball2 = self.create_circle_collider_object(50)
        self.ball2.add_component(RigidBody())
        self.ball2.transform.position = Vector2(700, 300)
        self.ball2.rigid_body.velocity = Vector2(-200, 50)
        self.ball2.rigid_body.mass = 10
        self.ball2.rigid_body.gravity_scale = 1
        self.ball2.collider.restitution = 1

        box_image = pygame.Surface((300, 50)).convert()
        box_image.fill((150, 150, 150))
        self.box = self.create_game_object(box_image)
        self.box.transform.position = Vector2(200, h - 250)
        self.box.renderer.depth = -5
        self.box.collider.restitution = 0.7

        floor_image = pygame.Surface((w, 200)).convert()
        floor_image.fill((50, 50, 50))

        self.floor = self.create_game_object(floor_image)
        self.floor.transform.position = Vector2(w/2, h-100)
        self.floor.collider.restitution = 0.7

        # Create the wall entities and set their collision boxes.
        # Make these wall thick, so the ball doesn't escape from the level.
        self.topWall = self.create_box_collider_object(w*2, 200)
        self.leftWall = self.create_box_collider_object(200, h*2)
        self.rightWall = self.create_box_collider_object(200, h*2)

        # set up wall positions
        self.topWall.transform.position = Vector2(w/2, 0-80)
        self.leftWall.transform.position = Vector2(0, h/2-50)
        self.rightWall.transform.position = Vector2(w, h/2+50)


engine.set_world(PlatformWorld())
engine.run()
