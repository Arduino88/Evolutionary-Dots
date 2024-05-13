import pygame
import random
import math
import copy
import numpy as np
from pygame import Color

random.seed(4)

dotColor = Color('white')

goalColor = Color('red')

wallColor = Color('blue')

totalMutations = 0

dotSize = 5
goalSize = 30

accLimit = 1
speedLimit = 1.5

screenWidth = 1500
screenHeight = 800

bestDotColor = Color("green")
dotStartPos = np.array([20, screenHeight / 2])

class Wall:
    def __init__(self, color, width, pos, height) -> None:
        self.color = color
        self.width = width
        self.height = height
        self.pos = pos


    def draw(self, screen):
        pygame.draw.rect(screen, wallColor, (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def checkCollision(self, dot):
        if dot.pos[0] >= self.pos[0] and dot.pos[0] < (self.pos[0] + self.width) and dot.pos[1] >= self.pos[1] and dot.pos[1] < (self.pos[1] + self.height):
            dot.dead = True

class Goal:
    def __init__(self, pos: tuple):
        self.pos = np.array([pos[0], pos[1]])

    def draw(self, screen):
        pygame.draw.circle(screen, goalColor, (int(self.pos[0]), int(self.pos[1])), goalSize)

class Brain:
    def __init__(self, size):
        self.step = 0
        self.size = size
        self.directions = []

    def randomize(self):
        for i in range(self.size):
            randomAngle = random.uniform(-1, 1) * math.pi / 2
            self.directions.append(np.array([math.cos(randomAngle) * random.choice((-1, 1)), math.sin(randomAngle) * random.choice((-1, 1))]))

    def clone(self, bestDot: bool):
        clone = Brain(size = self.size)
        mutationRate = 0.005
        noiseFactor = 0.2
        if bestDot:
            for value in self.directions:
                clone.directions.append(value)
            return clone
        for i, direction in enumerate(self.directions):
            rand = random.random()

            if rand < mutationRate and not bestDot:
                noise = np.random.normal(0, 2, len(direction))
                newDirection = np.array([direction[0], direction[1]])
                #add noise to direction
                newDirection = direction + noise * noiseFactor
                
                #print(f'mutating...\n {direction} -> {newDirection}, parent fitness: {parentFitness}')

                """randomAngle = random.uniform(-1, 1) * math.pi / 2
                newDirection[0] = math.cos(randomAngle) * random.choice((-1, 1))
                newDirection[1] = math.sin(randomAngle) * random.choice((-1, 1))"""
                clone.directions.append(newDirection)
                global totalMutations
                totalMutations += 1
                #print(totalMutations, "directionIndex:", i, "Length of Directions:", len(self.directions))
            else:
                clone.directions.append(direction)
            


        #print (self.directions[0], clone.directions[0])
        return clone
    

class Dot:
    def __init__(self):
        self.dead = False
        self.fitness = float()
        self.reachedGoal = False
        self.stepsExhausted = False
        self.brain = Brain(600)
        self.pos = dotStartPos
        self.vel = np.array([0.0, 0.0])
        self.acc = np.array([0.0, 0.0])

    def draw(self, screen, paramColor, size):
        #print(self.pos)
        pygame.draw.circle(screen, paramColor, self.pos, size)

    def move(self, goalPos):
        if self.brain.step >= len(self.brain.directions):
            self.dead = True
            self.stepsExhausted = True
        if not self.dead and not self.reachedGoal:
            self.acc = self.brain.directions[self.brain.step]
            self.brain.step += 1
            accVectorMagnitude = math.sqrt((math.sin(self.acc[0])) ** 2 + (math.cos(self.acc[1])) ** 2)
            if accVectorMagnitude > accLimit:
                accRatio = (accLimit / accVectorMagnitude)
                self.acc *= accRatio

            velVectorMagnitude = math.sqrt((math.sin(self.vel[0])) ** 2 + (math.cos(self.vel[1])) ** 2)
            if velVectorMagnitude > speedLimit:
                velRatio = (speedLimit / velVectorMagnitude)
                self.vel *= velRatio

            self.vel += self.acc
            self.pos += self.vel
        
            if self.pos[0] < 0 or self.pos[0] > screenWidth or self.pos[1] < 0 or self.pos[1] > screenHeight:
                self.dead = True

            elif np.linalg.norm(self.pos - goalPos) < goalSize:
                self.reachedGoal = True

            elif self.dead and not self.stepsExhausted:
                self.fitness * 10 ** -((len(self.brain.directions) - self.brain.step) * 10 ** -2)

    def calculateFitness(self, goal: Goal):
        distanceToGoalNumpy = self.pos - goal.pos
        distanceToGoal = math.sqrt((distanceToGoalNumpy[0] ** 2 + distanceToGoalNumpy[1] ** 2))
        #print("DISTANCE TO GOAL", distanceToGoal)
        if self.fitness is not None:
            temp = 1 / (distanceToGoal ** 2)
            if temp >= self.fitness:
                self.fitness = temp
        if self.reachedGoal:
            print(f'Goal Reached, fitness increasing from {self.fitness} to {self.fitness * (len(self.brain.directions) - self.brain.step)}')
            self.fitness = (len(self.brain.directions) - self.brain.step) ** 2

        #print("FITNESS", self.fitness)

    def getChild(self):
        child = Dot()
        child.brain = self.brain.clone(bestDot=False)
        return child
    
    def printStats(self):
        print(f'BRAIN: step {self.brain.step}, directions length {len(self.brain.directions)}, \nPHYSICS: pos {self.pos}, vel {self.vel}, dead? {self.dead}, reachedGoal? {self.reachedGoal}, stepsExhausted? {self.stepsExhausted}')


class DotsGame:
    def __init__(self, count: int, startPos, goalPos):
        self.gen = 1
        self.running = True
        self.startPos = startPos
        self.count = count
        self.dots = []
        self.highestFitness = 0
        self.goal = Goal(goalPos)
        self.wall1 = Wall(wallColor, width=60, pos=np.array([800, 0]), height = 500)
        self.wall2 = Wall(wallColor, width=60, pos=np.array([200, 200]), height = 800)
        self.wall3 = Wall(wallColor, width=60, pos=np.array([1000, 400]), height = 800)
        self.wall4 = Wall(wallColor, width=400, pos=np.array([1000, 400]), height = 60)

        self.initializeDots()

        self.bestDot = self.dots[0]


    def initializeDots(self):
        for i in range(self.count):
            self.dots.append(Dot())


        for dot in self.dots:
            dot.fitness = 0.0
            dot.brain.randomize()


    def updateDots(self, screen):
        if self.allDotsDead():
            self.running = False
        self.updateScreen(screen)
        self.goal.draw(screen)
        self.wall1.draw(screen)
        self.wall2.draw(screen)
        self.wall3.draw(screen)
        self.wall4.draw(screen)

        for i, dot in enumerate(self.dots):
            dot.move(self.goal.pos)
            #self.wall1.checkCollision(dot)
            #self.wall2.checkCollision(dot)
            self.wall3.checkCollision(dot)
            self.wall4.checkCollision(dot)
            if i == self.count:
                #print('best dot directions - LIST:', dot.brain.directions[0])
                #print('\nBEST DOT STATS:')
                #self.bestDot.printStats()
                #print('\nLAST DOT IN LIST STATS:')
                #dot.printStats()
                dot.draw(screen, bestDotColor, dotSize)
            elif not dot.dead:
                dot.draw(screen, dotColor, dotSize)

    def updateScreen(self, screen):
        pygame.draw.rect(screen,(100, 100, 90), [0, 0, screenWidth, screenHeight])

    def allDotsDead(self):
        for dot in self.dots:
            if not dot.dead and not dot.reachedGoal:
                return False
        return True
    
    def naturalSelection(self):
        newDots = []
        self.calculateFitnessSum()

        for i in range(self.count):
            #select parent based on fitness
            parent = self.selectParent()
        
            #create new child based on parent
            newDots.append(parent.getChild())

        newDots.append(self.bestDot)
        self.dots = newDots
        
        for dot in self.dots:
            #print(f'Dots count: {len(self.dots)}', dot.brain.directions[0])
            dot.pos = self.startPos
            dot.brain.step = 1
        self.gen += 1
        #print(f'best dot directions - bestDot:', self.bestDot.brain.directions[0])
        #print(self.count, len(self.dots))
        #print(f'generation finished... \nnow starting generation {self.gen}.')
            
    def calculateFitness(self):
        #newList = []
        for dot in self.dots:
            dot.calculateFitness(self.goal)
            #newList.append(dot.fitness)
        #print(dot.fitness, "TEST DOT FITNESS")
        #newList.sort()
        #print(newList)
        #print(f'max: {max(newList)}, min: {min(newList)}')

    def calculateFitnessSum(self):
        self.fitnessSum = 0
        for dot in self.dots:
            self.fitnessSum += dot.fitness

    def selectParent(self) -> Dot:
        rand = random.random() * self.fitnessSum
        runningSum = 0
        for dot in self.dots:
            runningSum += dot.fitness
            if runningSum > rand:
                return dot
            
        print('BAD THINGS HAPPENING')
        return None
    
    def updateBestDot(self):
        self.highestFitness = 0
        for dot in self.dots:
            #print(dot.fitness, "<", self.highestFitness, '==', self.bestDot.fitness)
            if dot.fitness > self.highestFitness:
                newDot = Dot()
                newDot.brain = copy.deepcopy(dot.brain)
                self.bestDot = newDot
                self.highestFitness = dot.fitness
                #print(self.highestFitness, '<-- highest fitness updated')
                

    def resetFinalDot(self):
        self.dots[-1].dead = False
        self.dots[-1].vel = np.array([0.0, 0.0])
        self.dots[-1].acc = np.array([0.0, 0.0])
        self.dots[-1].pos = self.startPos   


def main():

    pygame.init()
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    mainGame = DotsGame(200, (10, screenHeight / 2), goalPos=(screenWidth - 180, screenHeight / 2 + 130))
    screen.fill(Color('black'))
    mainGame.updateBestDot()


        #event loop
    while mainGame.running:

        
        mainGame.goal.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainGame.running = False

        if mainGame.allDotsDead():
            print("ALL DOTS DEAD")
            



            mainGame.calculateFitness()
            mainGame.updateBestDot()
            mainGame.naturalSelection()
            mainGame.resetFinalDot()

            

        else:
            mainGame.calculateFitness()
            mainGame.updateDots(screen)
            pygame.display.flip()

        pygame.time.delay(10)



if __name__=="__main__":
    main()