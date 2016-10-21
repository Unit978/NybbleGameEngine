

from world import *
from engine import *

engine = Engine(1200, 700)


class ShootingRange(World):

    def __init__(self):

        super(ShootingRange, self).__init__()

    def load_scene(self):
        pass

s = ShootingRange()
engine.set_world(s)
engine.worlds.append(s)
engine.run()
