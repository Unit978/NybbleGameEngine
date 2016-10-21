

from world import *
from engine import *
from entity import *
from components import BehaviorScript

from math import sin

engine = Engine(1200, 700)


class TargetBehavior(BehaviorScript):

    def __init__(self, script_name):
        super(TargetBehavior, self).__init__(script_name)

        self.direction = 1
        self.speed = 100

    def update(self):

        engine = self.entity.world.engine
        transform = self.entity.transform

        min_extent = 100
        max_extent = engine.display.get_size()[0] - min_extent

        if transform.position.x > max_extent:
            transform.position.x = max_extent
            self.entity.rigid_body.velocity *= -1.0
            self.direction = -1

        elif transform.position.x < min_extent:
            transform.position.x = min_extent
            self.entity.rigid_body.velocity *= -1.0
            self.direction = 1


class Life(BehaviorScript):

    def __init__(self, script_name, life):

        super(Life, self).__init__(script_name)

        self.life = life
        self.timer = 0.0

    def update(self):

        self.timer += self.entity.world.engine.delta_time

        if self.timer >= self.life:
            self.entity.world.destroy_entity(self.entity)


class Shoot(BehaviorScript):

    def __init__(self, script_name):
        super(Shoot, self).__init__(script_name)

        self.firing_rate = 0.5
        self.firing_timer = 0.0

        self.target = None

        self.bullet_speed = 300

    def update(self):

        if self.target is None:
            return

        engine = self.entity.world.engine

        self.firing_timer += engine.delta_time

        if self.firing_timer >= self.firing_rate:
            self.fire()
            self.firing_timer = 0.0

    def fire(self):

        blue = RenderSystem.create_solid_image(5, 5, (0, 50, 255))
        bullet = self.entity.world.create_game_object(blue)
        bullet.add_component(RigidBody())
        bullet.add_script(Life("life", 2.0))

        pos = self.entity.transform.position
        bullet.transform.position = Vector2(pos.x, pos.y)

        to_target = Vector2.get_normal(self.target.transform.position - pos)
        bullet.rigid_body.velocity = to_target * self.bullet_speed

    def target_lead(self):

        target = self.target
        transform = self.entity.transform

        # The displacement between the game object and the target
        to_target_disp = target.transform.position - transform.position


class ShootingRange(World):

    def __init__(self):

        super(ShootingRange, self).__init__()

    def load_scene(self):

        # setup background
        size = self.engine.display.get_size()
        w = size[0]
        h = size[1]
        back_img = RenderSystem.create_solid_image(w, h, (28, 5, 42))
        back = self.create_renderable_object(back_img, Vector2(0, 0))
        back.renderer.depth = 100

        # setup target
        orange = RenderSystem.create_solid_image(20, 20, (255, 100, 0))
        target = self.create_game_object(orange)
        target.add_component(RigidBody(Vector2(100, 0)))
        target.transform.position = Vector2(100, 100)
        target.collider.is_trigger = True

        target.add_script(TargetBehavior("target behavior"))

        # setup turret
        red = RenderSystem.create_solid_image(20, 20, (255, 0, 0))
        turret = self.create_renderable_object(red)
        turret.transform.position = Vector2(size[0] / 2, size[1] / 2)

        shoot_script = Shoot("shoot")
        shoot_script.target = target
        turret.add_script(shoot_script)


s = ShootingRange()
engine.set_world(s)
engine.worlds.append(s)
engine.run()
