import pygame
import random
import math
import numpy as np
from pygame import Color

global dotColor
dotColor = Color('white')

goalColor = Color('red')

global dotSize
dotSize = 3

global speedLimit
speedLimit = 2

screenWidth = 1500
screenHeight = 600

class Goal:
    def __init__(self, x, y):
        self.pos = np.array([x, y])

    def draw(self, screen):
        pygame.draw.circle(screen, goalColor, (int(self.pos[0]), int(self.pos[1])), dotSize)

class Brain:
    def __init__(self, size):
        self.step = 0
        self.size = size
        self.directions = []
        self.randomize()

    def randomize(self):
        for i in range(self.size):
            randomAngle = random.uniform(-1, 1) * math.pi / 2
            self.directions.append(np.array([math.cos(randomAngle) * random.choice((-1, 1)), math.sin(randomAngle) * random.choice((-1, 1))]))

class Dot:
    def __init__(self, pos):
        self.dead = False
        fitness = 0
        self.brain = Brain(400)
        self.pos = pos
        self.color = Color(dotColor)
        self.pos = pos
        self.vel = np.array([0.0, 0.0])
        self.acc = np.array([0.0, 0.0])

    def draw(self, screen):
        #print(self.pos)
        pygame.draw.circle(screen, self.color, self.pos, dotSize)

    def move(self):
        self.acc = self.brain.directions[self.brain.step]
        if self.brain.step >= len(self.brain.directions):
            self.dead = True
        if not self.dead:
            self.brain.step += 1
            if not math.sqrt((math.sin(self.vel[0] + self.acc[0])) ** 2 + (math.cos(self.vel[1] + self.acc[1])) ** 2) > speedLimit:
                self.vel += self.acc
                self.pos += self.vel
            
            if self.pos[0] < 0 or self.pos[0] > screenWidth or self.pos[1] < 0 or self.pos[1] > screenHeight:
                self.dead = True

    def calculateFitness(self, goal: Goal):
        distanceToGoal = np.linalg.norm(self.pos - goal.pos)
        #print(distanceToGoal)
        self.fitness = 1.0 / distanceToGoal ** 2


class DotsGame:
    def __init__(self, count: int, startPos):
        self.running = True
        self.startPos = startPos
        self.count = count
        self.dots = []

        self.initializeDots()


    def initializeDots(self):
        for i in range(self.count):
            self.dots.append(Dot((self.startPos[0], self.startPos[1])))

    def updateDots(self, screen, goal):
        for dot in self.dots:
            dot.move()
            dot.draw(screen)
            dot.calculateFitness(goal)

    def allDotsDead(self):
        for dot in self.dots:
            if dot.dead == False:
                return False
        return True

def main():

    pygame.init()
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    mainGame = DotsGame(200, (10, screenHeight / 2))
    screen.fill(Color('black'))
    goal = Goal(screenWidth - 50, screenHeight - 50)

        #event loop
    while mainGame.running:

        pygame.draw.rect(screen,(100, 100, 90), [0, 0, screenWidth, screenHeight])
        goal.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainGame.running = False


        if mainGame.allDotsDead():
            mainGame.running = False

        mainGame.updateDots(screen, goal)
        pygame.display.flip()

        pygame.time.delay(10)



if __name__=="__main__":
    main()