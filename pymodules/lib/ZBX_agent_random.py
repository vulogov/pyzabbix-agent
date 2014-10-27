##
## Sample agent which loads during startup and generates random numbers
##
import random

class Agent:
    def __init__(self, ctx):
        self.ctx = ctx
        random.seed()
    def desc(self):
        return "Generating random numbers"
    def random(self, ctx):
        return random.random()
