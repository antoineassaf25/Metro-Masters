"""This file is what is run to start the program. This files mainly includes
    Mode Handling (self-made)
    2D Visuals
    Collisions
    Power Ups
    Contains many core-game attributes"""


# from https://www.diderot.one/course/34/chapters/2808/#anchor-segment-214904
from cmu_112_graphics import * #ModalApp, App, Mode


from Geometry import *
from Runner import *
from DataManagement import *


#from built-in functions into Python 3.85
import copy
import math
import random

"""IMPORTANT CREDENTIAL NOTICE:
    ALL IMAGES WERE SELF-DRAWN BY ANTOINE ASSAF (CREATOR OF GAME)
"""

#from @B2-1-33 www.diderot.one/course/34/chapters/2605/#anchor-atom-186051
def distance(x0, y0, x1, y1):
    return math.sqrt((x0 - y0)**2 + (x1 - y1)**2)

#from @B0-1-56 www.diderot.one/course/34/chapters/2288/#anchor-atom-188353 
def almostEqual(d1, d2, epsilon=10**-7):
    return (abs(d2 - d1) < epsilon)

#from @B0-8-115 www.diderot.one/course/34/chapters/2604/#anchor-atom-189700
def readFile(path):  
    with open(path, "rt") as f:  
        return f.read()  

#from @B0-8-115 www.diderot.one/course/34/chapters/2604/#anchor-atom-189700
def writeFile(path, contents):  
    with open(path, "wt") as f:  
        f.write(contents)  

class MetroMastersApp(App):
    def appStarted(self):

        #essentially I will need to craft a make-shift ModalApp because the one provided by CMU lags
        self.currentMode = "home"

        self.cx = self.width/2
        self.cy = self.height/2

        self.transitioning = False
        self.toMode = "home" #default
        self.transitionFrame = 0
        self.transitionFrames = 6
        self.dF = 1

        self.personalHighest = 0

        self.defaultHorizonLevel = self.height/4
        self.focus = [self.width/2,self.defaultHorizonLevel]
        self.timerDelay = 25
        self.cameraPos = [0,0]
        self.scrollZ = self.timeElapsed = self.score = self.coinsCollected = 0
        self.multiplier = 1
        self.objects = []
        self.coins = []
        self.planks = []
        self.runner = Runner(self, "black")
        self.storedOldCameraPos = self.laneSwitchTime = 0
        self.storedOldCameraFoc = self.focus[0]
        self.levelHeight = .35 #how tall is the graphic for each level
        self.gravity = -2.5
        self.speed = .055
        self.oldSpeed = 0
        self.difficulty = 1 #goes up to 5
        self.map = random.choice(["MALIBU", "GOLDEN GATE BRIDGE"])
        self.possibleMoves = [
                                "TRAIN0", "TRAIN1", "TRAIN2",
                                "LADDER0", "LADDER1", "LADDER2",
                                "DUCK0", "DUCK1", "DUCK2",
                                "JUMP0", "JUMP1", "JUMP2"]
        self.allPowerUps = ["AI","SPEEDY BOOTS", "DOUBLE POINTS","MAGNET"] 
        self.mouseDragPos = [[None, None],[None, None]] #start drag position, end drag position

        #this essentially locates where the objects are (z where player is). There are 18 "locations" an object can be in
        #for each lane
            #there is are two levels (on ground or on train)
                #An object can be hurt someone jumping, running, or ducking
        #True means an object exists there
        self.collisionBox = [
            [[False, False, False],[False, False, False]], 
            [[False, False, False],[False, False, False]],
            [[False, False, False],[False, False, False]]]

        #images (ALL IMAGES ARE SELF-DRAWN BY ANTOINE ASSAF)
        self.background = self.loadImage('Background.png')
        self.background = self.scaleImage(self.background, 5)
        self.logo = self.loadImage("Logo.png")
        self.logo = self.scaleImage(self.logo, 1.75)
        self.button1 = self.loadImage('Button1.png')
        self.button2 = self.loadImage('Button2.png')
        self.button3 = self.loadImage('Button3.png')
        self.button1 = self.scaleImage(self.button1, .75)
        self.button2 = self.scaleImage(self.button2, .75)
        self.button3 = self.scaleImage(self.button3, .75)
        self.magnetImage = self.loadImage('Magnet.png')
        self.speedyBootsImage = self.loadImage('SpeedyBoots.png')
        self.multiplierImage = self.loadImage('Multiplier.png')
        self.AIImage = self.loadImage('AI.png')
        self.magnetImage = self.scaleImage(self.magnetImage, .65)
        self.AIImage = self.scaleImage(self.AIImage, .65)
        self.speedyBootsImage = self.scaleImage(self.speedyBootsImage, .65)
        self.multiplierImage = self.scaleImage(self.multiplierImage, .65)

    def createTrain(self, lane, trainLength = .3, speed = .03):    
        if lane == 0:
            p1 = Point(self, .025, 1, 1.14)
            p2 = Point(self, .3, 1, 1.14)
            p3 = Point(self, .3, 1, 1.14 + trainLength)
            p4 = Point(self, .025, 1, 1.14 + trainLength)
        elif lane == 1:
            p1 = Point(self, .5-(.275/2), 1, 1.14)
            p2 = Point(self, .5+(.275/2), 1, 1.14)
            p3 = Point(self, .5+(.275/2), 1, 1.14 + trainLength)
            p4 = Point(self, .5-(.275/2), 1, 1.14 + trainLength)
        elif lane == 2:
            p1 = Point(self, 1-.025, 1, 1.14)
            p2 = Point(self,.7, 1, 1.14)
            p3 = Point(self, .7, 1, 1.14 + trainLength)
            p4 = Point(self, 1-.025, 1, 1.14 + trainLength)

        color = random.choice(["cyan", "purple"])
        surfaces = []
        surfaces += [Surface(self, [p1, p2, p3, p4], color)]

        return Train(self, surfaces, 0, self.levelHeight, lane, speed)

    def createTunnel(self, tunnelLength = .1, speed = 0):

        tunnelObjects = []

        p1 = Point(self, -.5, 1, 1.14)
        p2 = Point(self, -.1, 1, 1.14)
        p3 = Point(self, -.1, 1, 1.14 + tunnelLength)
        p4 = Point(self, -.5, 1, 1.14 + tunnelLength)

        surfaces = []
        color = "gray"
        
        tunnelObjects += [Decoration(self, [Surface(self, [p1, p2, p3, p4], color)], 0, self.levelHeight*3, -1, 0)]

        p1 = Point(self, 1.1, 1, 1.14)
        p2 = Point(self, 1.5, 1, 1.14)
        p3 = Point(self, 1.5, 1, 1.14 + tunnelLength)
        p4 = Point(self, 1.1, 1, 1.14 + tunnelLength)

        tunnelObjects += [Decoration(self, [Surface(self, [p1, p2, p3, p4], color)], 0, self.levelHeight*3, 3, 0)]

        height = self.levelHeight * 3
        p1 = Point(self, -.5, 1, 1.14,h = height)
        p2 = Point(self, 1.5, 1, 1.14, h = height)
        p3 = Point(self, 1.5, 1, 1.14 + tunnelLength, h = height)
        p4 = Point(self, -.5, 1, 1.14 + tunnelLength, h = height)

        tunnelObjects += [Decoration(self, [Surface(self, [p1, p2, p3, p4], color)], 0, height + self.levelHeight, 1, 0)]

        return tunnelObjects

    def createBridge(self, houseLength = .025, speed = 0):

        houseObjects = []
        
        color = "red"

        p1 = Point(self, -1.75, 1, 1.14)
        p2 = Point(self, -1.25, 1, 1.14)
        p3 = Point(self, -1.25, 1, 1.14 + houseLength)
        p4 = Point(self, -1.75, 1, 1.14 + houseLength)
        
        houseObjects += [Decoration(self, [Surface(self, [p1, p2, p3, p4], color)], 0, self.levelHeight*10, -2, 0, False)]

        p1 = Point(self, 2.25, 1, 1.14)
        p2 = Point(self, 2.75, 1, 1.14)
        p3 = Point(self, 2.75, 1, 1.14 + houseLength)
        p4 = Point(self, 2.25, 1, 1.14 + houseLength)

        
        houseObjects += [Decoration(self, [Surface(self, [p1, p2, p3, p4], color)], 0, self.levelHeight*10, 4, 0, False)]

        return houseObjects


    def createLadder(self, lane, barrierLength = .05, speed = .03):

        ladderObjects = []
        height = -.06
        for i in range(-1, 4, 2):
            height += .12
            if lane == 0:
                p1 = Point(self, .025, 1, 1.14 - barrierLength, h = height)
                p2 = Point(self, .3, 1, 1.14 - barrierLength, h = height)
                p3 = Point(self, .3, 1, 1.14, h = height)
                p4 = Point(self, .025, 1, 1.14, h = height)
            elif lane == 1:
                p1 = Point(self, .5-(.275/2), 1, 1.14 - barrierLength, h = height)
                p2 = Point(self, .5+(.275/2), 1, 1.14 - barrierLength, h = height)
                p3 = Point(self, .5+(.275/2), 1, 1.14, h = height)
                p4 = Point(self, .5-(.275/2), 1, 1.14,h = height)
            elif lane == 2:
                p1 = Point(self, 1-.025, 1, 1.14+barrierLength,h = height)
                p2 = Point(self,.7, 1, 1.14+barrierLength,h = height)
                p3 = Point(self, .7, 1, 1.14,h = height)
                p4 = Point(self, 1-.025, 1, 1.14,h = height)

            color = random.choice(["grey"])
            surfaces = []
            surfaces += [Surface(self, [p1, p2, p3, p4], color)]
            if i == -1:
                ladderObjects += [Ladder(self, surfaces, 0, height + .04, lane, speed)]  
            else:
                ladderObjects += [Ladder(self, surfaces, 0, height + .04, lane, speed)]               



        return ladderObjects
    
    def createJumpBarrier(self, lane, barrierLength = .05):
        if lane == 0:
            p1 = Point(self, .025, 1, 1.14)
            p2 = Point(self, .3, 1, 1.14)
            p3 = Point(self, .3, 1, 1.14 + barrierLength)
            p4 = Point(self, .025, 1, 1.14 + barrierLength)
        elif lane == 1:
            p1 = Point(self, .5-(.275/2), 1, 1.14)
            p2 = Point(self, .5+(.275/2), 1, 1.14)
            p3 = Point(self, .5+(.275/2), 1, 1.14 + barrierLength)
            p4 = Point(self, .5-(.275/2), 1, 1.14+ barrierLength)
        elif lane == 2:
            p1 = Point(self, 1-.025, 1, 1.14)
            p2 = Point(self,.7, 1, 1.14)
            p3 = Point(self, .7, 1, 1.14 + barrierLength)
            p4 = Point(self, 1-.025, 1, 1.14 + barrierLength)

        color = random.choice(["pink"])
        surfaces = []
        surfaces += [Surface(self, [p1, p2, p3, p4], color)]

        return JumpBarrier(self, surfaces, 0, .2, lane, 0)

    def createDuckBarrier(self, lane, barrierLength = .05):
        height = .2
        if lane == 0:
            p1 = Point(self, .025, 1, 1.14, h = height)
            p2 = Point(self, .3, 1, 1.14,h = height)
            p3 = Point(self, .3, 1, 1.14 + barrierLength,h = height)
            p4 = Point(self, .025, 1, 1.14 + barrierLength,h = height)
        elif lane == 1:
            p1 = Point(self, .5-(.275/2), 1, 1.14,h = height)
            p2 = Point(self, .5+(.275/2), 1, 1.14,h = height)
            p3 = Point(self, .5+(.275/2), 1, 1.14 + barrierLength,h = height)
            p4 = Point(self, .5-(.275/2), 1, 1.14+ barrierLength,h = height)
        elif lane == 2:
            p1 = Point(self, 1-.025, 1, 1.14,h = height)
            p2 = Point(self,.7, 1, 1.14,h = height)
            p3 = Point(self, .7, 1, 1.14 + barrierLength,h = height)
            p4 = Point(self, 1-.025, 1, 1.14 + barrierLength,h = height)

        color = random.choice(["red"])
        surfaces = []
        surfaces += [Surface(self, [p1, p2, p3, p4], color)]
        part1 = DuckBarrier(self, surfaces, 0, height + .2, lane, 0)

        if lane == 0:
            p1 = Point(self, .025, 1, 1.14)
            p2 = Point(self, .05, 1, 1.14)
            p3 = Point(self, .05, 1, 1.14 + barrierLength)
            p4 = Point(self, .025, 1, 1.14 + barrierLength)
        elif lane == 1:
            p1 = Point(self, .5-(.275/2), 1, 1.14)
            p2 = Point(self, .5-(.275/2) + .025, 1, 1.14)
            p3 = Point(self, .5-(.275/2) + .025, 1, 1.14 + barrierLength)
            p4 = Point(self, .5-(.275/2), 1, 1.14+ barrierLength)
        elif lane == 2:
            p1 = Point(self, 1-.025, 1, 1.14)
            p2 = Point(self,1-.05, 1, 1.14)
            p3 = Point(self, 1-.05, 1, 1.14 + barrierLength)
            p4 = Point(self, 1-.025, 1, 1.14 + barrierLength)

        color = random.choice(["red"])
        surfaces = []
        surfaces += [Surface(self, [p1, p2, p3, p4], color)]
        part2 = Decoration(self, surfaces, 0, height + .2, lane, 0)

        if lane == 0:
            p1 = Point(self, .3-.025, 1, 1.14)
            p2 = Point(self, .3, 1, 1.14)
            p3 = Point(self, .3, 1, 1.14 + barrierLength)
            p4 = Point(self, .3-.025, 1, 1.14 + barrierLength)
        elif lane == 1:
            p1 = Point(self, .5+(.275/2), 1, 1.14)
            p2 = Point(self, .5+(.275/2) - .025, 1, 1.14)
            p3 = Point(self, .5+(.275/2) - .025, 1, 1.14 + barrierLength)
            p4 = Point(self, .5+(.275/2), 1, 1.14+ barrierLength)
        elif lane == 2:
            p1 = Point(self, .7, 1, 1.14)
            p2 = Point(self,.725, 1, 1.14)
            p3 = Point(self, .725, 1, 1.14 + barrierLength)
            p4 = Point(self, .7, 1, 1.14 + barrierLength)

        color = random.choice(["red"])
        surfaces = []
        surfaces += [Surface(self, [p1, p2, p3, p4], color)]
        part3 = Decoration(self, surfaces, 0, height + .2, lane, 0) 

        return [part1, part2, part3]

    def createTrainWrapper(self, lane, speed):
        self.objects.insert(0,self.createTrain(lane, .3, speed))

    def createLadderWrapper(self, lane, speed):
        contents = self.createLadder(lane, .01, speed)
        for content in contents:
            try:
                self.objects.insert(12,content)
            except:
                self.objects.insert(1,content)

    def createTunnelWrapper(self):
        contents = self.createTunnel()
        for content in contents:
            self.objects.insert(0,content)

    def createBridgeWrapper(self):
        contents = self.createBridge()
        for content in contents:
            self.objects.insert(0,content)


    def createDuckBarrierWrapper(self, lane):
        contents = self.createDuckBarrier(lane, .01)
        for content in contents:
            self.objects.insert(0,content)

    def createJumpBarrierWrapper(self, lane):
        self.objects.insert(0,self.createJumpBarrier(lane, .01))

    def randomizeMoves(self):
        newOrder = []
        clone = copy.copy(self.possibleMoves)
        while len(clone) > 0:
            newOrder += [clone.pop(random.randint(0,len(clone)-1))]
        return newOrder

    def isLegal(self, moves):
        for move in moves:
            if moves.count(move) > 1:
                return False
        
        state = [[False, False, False], [False, False, False], [False, False, False]]

        for move in moves:
            lane = int(move[-1])
            if move.startswith("LADDER"):
                if state[lane] != [True, True, True]:
                    return False

            for loc, spot in enumerate(state[lane]):
                if move.startswith("TRAIN"):
                    if spot == True:
                        return False
                    else:
                        state[lane][loc] = True
                        if state == [[True, True, True], [True, True, True], [True, True, True]]:
                            return False
                elif move.startswith("DUCK"):
                    if str(loc) in '12':
                        if spot == True:
                            return False
                        else:
                            state[lane][loc] = True
                elif move.startswith("JUMP"):
                    if str(loc) in '01':
                        if spot == True:
                            return False
                        else:
                            state[lane][loc] = True
            
        return True

    #advanced recursive backtracking
    def generateSection(self, target, moves = None, number = 0):

        if moves == None:
            moves = []

        if number >= target:
            return moves

        scrambledMoves = self.randomizeMoves()

        for move in scrambledMoves:
            moves += [move]

            if self.isLegal(moves):
                result = self.generateSection(target, moves, number + 1)
                if result != None:
                    return result
            moves.remove(move)

        return None

        
    def timerFired(self):
        if self.transitioning == True:
            self.transitionFrame += self.dF

            if self.transitionFrame == self.transitionFrames:
                self.currentMode = self.toMode
    
                if self.toMode == "end":
                    self.endActivated()
                if self.toMode == "play":
                    self.appStarted()
                    self.currentMode = "play"
                    self.transitionFrame = self.transitionFrames
                    self.transitioning = True

                self.dF = -1
            
            if self.transitionFrame < 0:
                self.transitionFrame = 0
                self.dF = 1
                self.transitioning = False


        if self.currentMode == "play":
            if self.runner.alive:
                self.timeElapsed += self.timerDelay
                if self.runner.currentPowerUp == "DOUBLE POINTS":
                    self.score += int(self.timerDelay * self.multiplier * self.speed * 2)
                else:
                    self.score += int(self.timerDelay * self.multiplier * self.speed)
                self.scrollZ -= .3
                self.runner.powerUpTimeLeft = max(self.runner.powerUpTimeLeft - self.timerDelay, 0)
                if self.runner.powerUpTimeLeft <= 0 and self.runner.currentPowerUp != None:
                    if self.runner.currentPowerUp == "SPEEDY BOOTS":
                        self.runner.forceField = False #remove forcefield
                    if self.runner.currentPowerUp == "AI":
                        self.objects = []
                    self.runner.currentPowerUp = None

                renderedObjects = []
                objectsInSector = [[0,0],[0,0],[0,0]] #there a 6 sectors (2 per lane)

                for obj in self.objects:
                    
                    obj.changeDistance(-self.speed)
                    if not obj.visible:
                        obj.visible = True

                    frontPos, endPos, delPos = 0,0,0
                    
                    if isinstance(obj, Ladder):
                        frontPos, endPos, delPos = -11, -11.4, -15
                    elif isinstance(obj, Train):
                        frontPos, endPos, delPos = -11.1, -14, -15
                    elif isinstance(obj, JumpBarrier):
                        frontPos, endPos, delPos = -11.2, -11.4, -13
                    elif isinstance(obj, DuckBarrier):
                        frontPos, endPos, delPos = -11.2, -11.4, -13

                    level = None
                    
                    if obj.speed > 0: #if train collides with another object, stop it
                        if isinstance(obj, (Ladder, Train)):
                            for obj2 in self.objects:
                                if obj2.lane == obj.lane:
                                    if isinstance(obj2, (JumpBarrier, DuckBarrier, Train)):
                                        if .05 < abs(obj2.zDistance - obj.zDistance) < .1:
                                            if not(isinstance(obj, Ladder) and isinstance(obj2, Train)):
                                                obj.speed = 0

                    if endPos < obj.zDistance < frontPos:
                    
                        #first ignore all collisions in the lane
                        for i in range(2):
                            for j in range(3):
                                self.collisionBox[obj.lane][i][j] = False

                        #now determine where the collisions are
                        if isinstance(obj, (Train, Ladder)):
                            self.collisionBox[obj.lane][0][0] = True
                            self.collisionBox[obj.lane][0][1] = True
                            self.collisionBox[obj.lane][0][2] = True
                            level = 0
                                        
                        elif isinstance(obj, JumpBarrier):
                            self.collisionBox[obj.lane][0][0] = True
                            self.collisionBox[obj.lane][0][1] = True
                            level = 0
                        elif isinstance(obj, DuckBarrier):
                            self.collisionBox[obj.lane][0][1] = True
                            self.collisionBox[obj.lane][0][2] = True
                            level = 0

                        #special collisions (something else happens besides ending game)
                        if self.runner.currentLane == obj.lane:
                            if isinstance(obj, Ladder):
                                #puts the player on the top
                                for i in range(2):
                                    for j in range(3):
                                        if i == j == 1: #top row default stance:
                                            self.runner.collisionBox[obj.lane][i][j] = True
                                        else:
                                            self.runner.collisionBox[obj.lane][i][j] = False
                                self.runner.climbing = True
                                level = 0
                        
                        objectsInSector[obj.lane][level] += 1

                    if isinstance(obj, Decoration):
                        if obj.zDistance > -15: #in screen
                            renderedObjects += [obj]
                    else:
                        if obj.zDistance > delPos: #in screen
                            renderedObjects += [obj]
                self.objects = renderedObjects

                for i in range(3):
                    for j in range(2):
                        if objectsInSector[i][j] == 0: #if there are NO OTHER OBJECTS in the sector
                            for k in range(3):
                                self.collisionBox[i][j][k] = False

                renderedCoins = []
                for coin in self.coins:
                    coin.changeDistance(-self.speed)
                    if not coin.visible:
                        coin.visible = True
                    if coin.z > 0: #still on screen
                        renderedCoins += [coin]
                    else:
                        coinX, coinY = coin.coordinatesToAbsolute()
                        runnerX, runnerY = self.runner.coordinatesToAbsolute()
                        if coin.theText == "?":
                            if abs(runnerX-coinX) < coin.r*16 and abs(runnerY-coinY) < coin.r*16:
                                self.runner.currentPowerUp = random.choice(self.allPowerUps)
                                self.runner.powerUpTimeLeft = getUpgrade(self.runner.currentPowerUp)
                                if self.runner.currentPowerUp == "SPEEDY BOOTS":
                                    self.runner.forceField = True
                        else:
                            if self.runner.currentPowerUp == "MAGNET":
                                self.coinsCollected += 5
                            elif abs(runnerX-coinX) < coin.r*16 and abs(runnerY-coinY) < coin.r*16:
                                self.coinsCollected += 1

                self.coins = renderedCoins
            
                renderedPlanks = []
                for plank in self.planks:
                    plank.changeDistance(-self.speed)
                    if not plank.visible:
                        plank.visible = True
                    if plank.zDistance > -5: #still on screen
                        renderedPlanks += [plank]
                self.planks = renderedPlanks

                generateNow = int(self.timerDelay * (7-self.difficulty) * 20)

                if self.timeElapsed% generateNow == 0:
                    givenSection = self.generateSection(random.randint(max(self.difficulty-3, 1), self.difficulty))
                    prevSpeed = [0,0,0] #makes sure ladders are attached to front of trains
                    for move in givenSection:
                        chooseLane = int(move[-1])
                        obj = move[:-1]
                        if obj == "TRAIN":
                            speed = random.randint(25, 35 + (max(self.difficulty-3,0) * 6))/1000
                            prevSpeed[chooseLane] = speed
                            self.createTrainWrapper(chooseLane, speed)
                        elif obj == "LADDER":
                            self.createLadderWrapper(chooseLane, prevSpeed[chooseLane])
                        elif obj == "JUMP":
                            self.createJumpBarrierWrapper(chooseLane)
                        elif obj == "DUCK":
                            self.createDuckBarrierWrapper(chooseLane)

                if self.timeElapsed%1000 == 0:
                    self.speed += .0005
                    if self.runner.currentPowerUp == "SPEEDY BOOTS":
                        if self.oldSpeed == 0:
                            self.oldSpeed = self.speed
                        self.speed = .16
                    else:
                        if almostEqual(self.speed, .1605):
                            self.speed = self.oldSpeed
                            self.oldSpeed = 0
                        self.speed = min(self.speed, .12)
                    
                    if self.speed < .02: self.difficulty = 1
                    elif self.speed < .04: self.difficulty = 1
                    elif self.speed < .06: self.difficulty = 2
                    elif self.speed < .08: self.difficulty = 3
                    elif self.speed < .1: self.difficulty = 4
                    else: self.difficulty = 5                

                if self.timeElapsed%500 == 0:
                    self.createRailPlanks()

                if self.timeElapsed%10000 == 0:
                    self.createTunnelWrapper()

                if self.timeElapsed%2000 == 100 and self.map == "GOLDEN GATE BRIDGE":
                    self.createBridgeWrapper()

                if self.timeElapsed%750 == 0:
                    if self.timeElapsed%24000 == 12000:
                        self.createPowerUp()
                    else:
                        self.createCoin()

                if self.runner.climbing:
                    self.runner.climbTick()
                if self.runner.jumping:
                    self.runner.jumpTick()
                elif self.runner.ducking:
                    self.runner.duckTick()
                else:
                    self.focus[1] = self.defaultHorizonLevel

                if self.runner.switchingLanes != 0:
                    if self.runner.currentPowerUp == "AI":
                        animTime = 90
                    else:
                        animTime = 100
                    distanceMoved = self.width/2.5
                    percentFinished = self.laneSwitchTime/animTime
                    self.laneSwitchTime += self.timerDelay
                    if percentFinished > 1:
                        percentFinished = 1
                    self.cameraPos[0] = self.storedOldCameraPos + self.runner.switchingLanes*distanceMoved*math.sin(percentFinished)
                    self.focus[0] = self.storedOldCameraFoc + self.runner.switchingLanes *distanceMoved*math.sin(percentFinished)*1.1 #1.1 = how much is the camera rotating?

                    if percentFinished == 1:
                        self.runner.switchingLanes = 0
                        self.laneSwitchTime = 0
                        self.storedOldCameraPos = self.cameraPos[0]
                        self.storedOldCameraFoc = self.focus[0]

                self.runner.checkFall()
                self.checkCollisions()

    def checkCollisions(self):
        #don't bother checking collisions if there is nothing to collide with!
        if self.collisionBox != [
            [[False, False, False],[False, False, False]], 
            [[False, False, False],[False, False, False]],
            [[False, False, False],[False, False, False]]]:
            if not self.runner.climbing:
                for i in range(3):
                    for j in range(2):
                        for k in range(3):
                            if self.collisionBox[i][j][k] == self.runner.collisionBox[i][j][k] == True:
                                if self.runner.currentPowerUp == "AI":
                                    if self.collisionBox[self.runner.currentLane][self.runner.fLevel] == [True, True, False]:
                                        self.movementInput("Up")
                                    elif self.collisionBox[self.runner.currentLane][self.runner.fLevel] == [False, True, True]:
                                        self.movementInput("Down")                                   
                                    elif self.collisionBox[self.runner.currentLane][self.runner.fLevel] == [True, True, True]:
                                        if self.runner.currentLane == 0:
                                            self.movementInput("Right")
                                        elif self.runner.currentLane == 1:
                                            if self.collisionBox[0][self.runner.fLevel] == [True, True, True]:
                                                self.movementInput("Right")
                                            else:
                                                self.movementInput("Left")
                                        elif self.runner.currentLane == 2:
                                            self.movementInput("Left")
                                else:
                                    if self.runner.forceField:
                                        self.runner.forceField = False
                                        self.objects = [] #clear everything
                                        if self.runner.currentPowerUp == "SPEEDY BOOTS":
                                            self.runner.currentPowerUp = None
                                    else:
                                        self.runner.alive = False
                                        self.toEnd()
                            elif self.runner.currentPowerUp == "AI":
                                if random.randint(1, 30) == 20:
                                    direction = random.choice(["Left","Right"])
                                    if direction == "Right" and self.runner.currentLane < 2 and self.collisionBox[self.runner.currentLane+1][self.runner.fLevel] == [False, False, False]:
                                        self.movementInput("Right")
                                    if direction == "Left" and self.runner.currentLane > 0 and self.collisionBox[self.runner.currentLane-1][self.runner.fLevel] == [False, False, False]:
                                        self.movementInput("Left")
                    
                                
            
        


    def movementInput(self, direction):
        if direction == "w" or direction == "Up":
            if not self.runner.jumping and not self.runner.ducking:
                self.runner.jumping = True
        if direction == "s" or direction == "Down":
            if not self.runner.jumping and not self.runner.ducking:
                self.runner.ducking = True
        if direction == "a" or direction == "Left":
            if self.runner.switchingLanes == 0 and self.runner.changeLane(-1):
                self.runner.switchingLanes = -1
        if direction == "d" or direction == "Right":
            if self.runner.switchingLanes == 0 and self.runner.changeLane(1):
                self.runner.switchingLanes = 1

    def keyPressed(self, event):
        if self.runner.currentPowerUp != "AI":
            self.movementInput(event.key)

    def createLanesAndRails(self):
        lanes = []
        rails = []
        laneWidth = 1/3 #fraction of total width
        railWidth = 1/27 #fraction of total width
        for i in range(3):
            if self.runner.currentPowerUp == "SPEEDY BOOTS":
                color = "cyan"
            elif self.runner.currentPowerUp == "DOUBLE POINTS":
                color = "yellow"
            elif self.runner.currentPowerUp == "MAGNET":
                color = "pink"
            else:
                color = "orange"
            if i%2 == 0:
                if self.runner.currentPowerUp == "SPEEDY BOOTS":
                    color = "cyan2"
                elif self.runner.currentPowerUp == "DOUBLE POINTS":
                    color = "gold"
                elif self.runner.currentPowerUp == "MAGNET":
                    color = "pink2"
                else:
                    color = "darkorange"
            x0 = (laneWidth)*i
            x1 = (laneWidth)*(i+1)
            lanes += [Surface(self, [Point(self, x0,1,0), Point(self, x1,1,0), Point(self, x1,1,1), Point(self, x0,1,1)], color)]

            color = "gray"
            rails += [Surface(self, [Point(self, x0 + railWidth,1,0), Point(self, x0 + 2*railWidth,1,0), Point(self, x0 + railWidth,1,1), Point(self, x0 + 2*railWidth,1,1)], color)]
            rails += [Surface(self, [Point(self, x1 - 2*railWidth,1,0), Point(self, x1 - railWidth,1,0), Point(self, x1 - railWidth,1,1), Point(self, x1 - 2*railWidth,1,1)], color)]
        
        if self.map == "GOLDEN GATE BRIDGE":
            lanes += [Surface(self, [Point(self, -6*laneWidth,1,0), Point(self, -2*laneWidth,1,0), Point(self, -2*laneWidth,1,1), Point(self, -6*laneWidth,1,1)], "red4")]
            lanes += [Surface(self, [Point(self, 1+2*laneWidth,1,0), Point(self, 1+6*laneWidth,1,0), Point(self, 1+6*laneWidth,1,1), Point(self, 1+2*laneWidth,1,1)], "red4")]
            lanes += [Surface(self, [Point(self, -2*laneWidth,1,0), Point(self, 0,1,0), Point(self, 0,1,1), Point(self, -2*laneWidth,1,1)], "seashell4")]
            lanes += [Surface(self, [Point(self, 1,1,0), Point(self, 1+laneWidth*2,1,0), Point(self, 1+laneWidth*2,1,1), Point(self, 1,1,1)], "seashell4")]

            lanes += [Surface(self, [Point(self, -4*laneWidth,-1.4,0), Point(self, -1.5*laneWidth,-1.4,0), Point(self, -1.5*laneWidth,-1.4,1), Point(self, -4*laneWidth,-1.4,1)], "red3")]
            lanes += [Surface(self, [Point(self, 1.5*laneWidth + 1,-1.4,0), Point(self, 4*laneWidth + 1,-1.4,0), Point(self, 4*laneWidth + 1,-1.4,1), Point(self, 1.5*laneWidth + 1,-1.4,1)], "red3")]
        elif self.map == "MALIBU":
            lanes += [Surface(self, [Point(self, -4*laneWidth,1,0), Point(self, -2*laneWidth,1,0), Point(self, -2*laneWidth,1,1), Point(self, -4*laneWidth,1,1)], "gold")]
            lanes += [Surface(self, [Point(self, 1+2*laneWidth,1,0), Point(self, 1+4*laneWidth,1,0), Point(self, 1+4*laneWidth,1,1), Point(self, 1+2*laneWidth,1,1)], "gold")]
            lanes += [Surface(self, [Point(self, -2*laneWidth,1,0), Point(self, 0,1,0), Point(self, 0,1,1), Point(self, -2*laneWidth,1,1)], "yellow green")]
            lanes += [Surface(self, [Point(self, 1,1,0), Point(self, 1+laneWidth*2,1,0), Point(self, 1+laneWidth*2,1,1), Point(self, 1,1,1)], "yellow green")]

            lanes += [Surface(self, [Point(self, -6*laneWidth,-1.4,0), Point(self, -1.5*laneWidth,-1.4,0), Point(self, -1.5*laneWidth,-1.4,1), Point(self, -6*laneWidth,-1.4,1)], "plum2")]
            lanes += [Surface(self, [Point(self, 1.5*laneWidth + 1,-1.4,0), Point(self, 6*laneWidth + 1,-1.4,0), Point(self, 6*laneWidth + 1,-1.4,1), Point(self, 1.5*laneWidth + 1,-1.4,1)], "plum2")]

        return lanes, rails

    def createCoin(self):
        newCoins = []

        laneWidth = 1/3
        newCoins += [FocusedCircle(self, (laneWidth/2)+(random.randint(0,2) *laneWidth), 1, .7, "$", 5, "yellow", .1)]
        
        self.coins += newCoins

    def createPowerUp(self):
        newCoins = []

        laneWidth = 1/3
        newCoins += [FocusedCircle(self, (laneWidth/2)+(random.randint(0,2) *laneWidth), 1, .7, "?", 8, "purple", .1,)]
        
        self.coins += newCoins

    def createRailPlanks(self):
        for i in range(3):
            color = "darkorange4"

            laneWidth = 1/3 #fraction of total width
            plankCut = 1/36
            plankThickness = .01

            x0 = (laneWidth)*i
            x1 = (laneWidth)*(i+1)
            
            start = .4 + i*.05
            
            surfaces = [Surface(self, [Point(self, x0 + plankCut,1,start), Point(self, x1-plankCut,1,start), Point(self, x1-plankCut,1,start+plankThickness), Point(self, x0+plankCut,1,start+plankThickness)], color)]
            self.planks += [rectPrism(self, surfaces, 0, 0)] #heightless

    #CLICKING BUTTONS
    def toPlay(self):
        if self.transitionFrame == 0:
            if readFile('Upgrades.txt') == "" or readFile('Currency.txt') == "" or readFile('HighScores.txt') == "":
                getCurrency()
                getUpgrade("SPEEDY BOOTS")
                if readFile('HighScores.txt') == "":
                    defaultNPCs = "Easy Lily-2500\nExpert Dexter-50000\nMaster Baxter-100000\nSkilled Jill-7000\nAdvanced Franz-20000\n"
                    writeFile('HighScores.txt', defaultNPCs)
                self.toMode = "instructions"
                self.transitionFrame = 0
                self.transitioning = True
            else:
                self.toMode = "play"
                self.transitionFrame = 0
                self.transitioning = True

    def toShop(self):
        if self.transitionFrame == 0:
            self.toMode = "shop"
            self.transitionFrame = 0
            self.transitioning = True

    def toHelp(self):
        if self.transitionFrame == 0:
            self.toMode = "help"
            self.transitionFrame = 0
            self.transitioning = True

    def toScores(self):
        if self.transitionFrame == 0:
            self.toMode = "scores"
            self.transitionFrame = 0
            self.transitioning = True

    def toEnd(self):
        if self.transitionFrame == 0:
            self.toMode = "end"
            self.transitionFrame = 0
            self.transitioning = True

    def toHome(self):
        if self.transitionFrame == 0:
            self.toMode = "home"
            self.transitionFrame = 0
            self.transitioning = True

    def upgradeSpeedyBoots(self):
        upgradePowerUp("SPEEDY BOOTS")

    def upgradeMagnet(self):
        upgradePowerUp("MAGNET")

    def upgradeDoublePoints(self):
        upgradePowerUp("DOUBLE POINTS")

    def upgradeAI(self):
        upgradePowerUp("AI")

    #modeActivated

    def endActivated(self):

        if readFile('HighScores.txt') == "":
            defaultNPCs = "Easy Lily-2500\nExpert Dexter-50000\nMaster Baxter-100000\nSkilled Jill-7000\nAdvanced Franz-20000\n"
            writeFile('HighScores.txt', defaultNPCs)

        newScore(self.score)
        self.personalHighest = getBestScore("You")
        changeCurrency(self.coinsCollected)





    #all code below here draws the graphics.. 
    # ALL MODES ARE IN HERE, TO FUTURE SELF, 
    # SO CODE MAY LOOK CHAOTIC (but in reality it isn't)


    def redrawAll(self, canvas):

        if self.currentMode == "home":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            canvas.create_image(self.cx, self.cy/2, image = ImageTk.PhotoImage(self.logo))

            buttonCenter = (self.cx/2, self.cy*1.2)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toPlay)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button1))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "START", font = f"Constantia 40")

            buttonCenter = (self.cx*1.5, self.cy*1.2)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toShop)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button2))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "SHOP", font = f"Constantia 40")

            buttonCenter = (self.cx/2, self.cy*1.8)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toScores)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button3))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "SCORES", font = f"Constantia 40")

            buttonCenter = (self.cx*1.5, self.cy*1.8)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toHelp)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button2))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "HELP", font = f"Constantia 40")



        elif self.currentMode == "instructions":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            buttonCenter = (self.cx, self.cy/6)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "INSTRUCTIONS", font = f"Constantia 60")
            theText = """You seem new here... Welcome to Metro Masters!
Use the arrow keys or WASD to navigate through the subways.
Jump using up arrow/w and Duck using down arrow/s!
Avoid getting hit by a train! The game will become faster and faster.
Pick up power ups (a purple '?') and reveal its mystery!
The trains will strategically become more difficult to surpass.
Collect coins in-game and level up your power ups in the shop! 
Try beating current NPC scores or beat your own!"""
            buttonCenter = (self.cx, self.cy)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = theText, font = f"Constantia 20")

            buttonCenter = (self.cx, self.cy*1.8)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toPlay)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button1))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "BEGIN!", font = f"Constantia 40")




        elif self.currentMode == "help":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            buttonCenter = (self.cx, self.cy/6)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "INSTRUCTIONS", font = f"Constantia 60")
            theText = """Use the arrow keys or WASD to navigate through the subways.\nJump using up arrow/w and Duck using down arrow/s!\nAvoid getting hit by a train! The game will become faster and faster.\nThe trains will strategically become more difficult to surpass.\nCollect coins in-game and level up your power ups in the shop! \nTry beating current NPC scores or beat your own!\n\nAI power up auto-runs the game for you!\nDouble Points doubles your multiplier!\nSpeedy Boots speeds up the game with a force field!\nMagnet auto-grabs coins and makes them worth more!"""
            buttonCenter = (self.cx, self.cy)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = theText, font = f"Constantia 20")

            buttonCenter = (self.cx, self.cy*1.8)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toHome)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button1))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "HOME", font = f"Constantia 40")




        elif self.currentMode == "end":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            buttonCenter = (self.cx, self.cy/6)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "CONGRATULATIONS!", font = f"Constantia 60")

            buttonCenter = (self.cx, self.cy/2)
            canvas.create_text(buttonCenter[0], buttonCenter[1], text = f"SCORE: {self.score}", font = f"Constantia 50", fill = "gray")
            canvas.create_text(buttonCenter[0], buttonCenter[1]+50, text = f"PERSONAL BEST: {self.personalHighest}", font = f"Constantia 30", fill = "pink")
            buttonCenter = (self.cx, self.cy)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = f"COINS: {self.coinsCollected}", font = f"Constantia 50")
            canvas.create_text(buttonCenter[0], buttonCenter[1]+43, text = f"TOTAL COINS: {getCurrency()}", font = f"Constantia 30", fill = "pink")

            buttonCenter = (self.cx/2, self.cy*1.4)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toPlay)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button1))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "RESTART", font = f"Constantia 40")

            buttonCenter = (self.cx*1.5, self.cy*1.6)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toShop)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button2))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "SHOP", font = f"Constantia 40")

            buttonCenter = (self.cx/2, self.cy*1.8)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toScores)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button3))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "SCORES", font = f"Constantia 40")




        elif self.currentMode == "scores":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            buttonCenter = (self.cx, self.cy/6)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "HIGH SCORES!", font = f"Constantia 60")
            buttonCenter = (self.cx, self.cy/2)

            canvas.create_rectangle(self.cx/4, self.cy/2.5, self.cx* (7/4), self.cy * (4.75/3), fill = "seashell3", width = 4)
            scores = listTopNScores(10)
            for i, content in enumerate(scores.split('\n')):
                canvas.create_text(buttonCenter[0], buttonCenter[1] + (i*50), text = content, font = f"Constantia 30")

            buttonCenter = (self.cx, self.cy*1.85)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toHome)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button3))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "HOME", font = f"Constantia 40")




        elif self.currentMode == "shop":
            canvas.create_image(self.cx, self.cy, image = ImageTk.PhotoImage(self.background))
            buttonCenter = (self.cx, self.cy/6)
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "ANT'S SHOP", font = f"Constantia 60")
            canvas.create_text(buttonCenter[0], buttonCenter[1]+80, text = f"COINS: {getCurrency()}", fill = "gold", font = f"Constantia 30")

            buttonCenter = (self.cx/3, self.cy*(2.5/4))
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.upgradeSpeedyBoots)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.speedyBootsImage))
            level = (getUpgrade("SPEEDY BOOTS")-10000)//2000
            cost = int(getUpgrade("SPEEDY BOOTS")/75)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + 675, buttonCenter[1] + 20, fill = "seashell3", width = 4, onClick = self.upgradeSpeedyBoots)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + (675-150)/6 * level + 150, buttonCenter[1] + 20, width = 4, fill = "limegreen", onClick = self.upgradeSpeedyBoots)
            if level == 6:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"MAXED", font = f"Constantia 20")  
            else:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"UPGRADE TO LVL {level} FOR {cost} COINS", font = f"Constantia 20")
            duration = getUpgrade("SPEEDY BOOTS")//1000
            canvas.create_text(buttonCenter[0]+400, buttonCenter[1]-45, text = f"DURATION: {duration} SECONDS", font = f"Constantia 15")  



            buttonCenter = (self.cx/3, self.cy*(3.75/4))
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.upgradeDoublePoints)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.multiplierImage))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "", font = f"Constantia 40")
            level = (getUpgrade("DOUBLE POINTS")-10000)//2000
            cost = int(getUpgrade("DOUBLE POINTS")/75)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + 675, buttonCenter[1] + 20, fill = "seashell3", width = 4, onClick = self.upgradeDoublePoints)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + (675-150)/6 * level + 150, buttonCenter[1] + 20, width = 4, fill = "limegreen", onClick = self.upgradeDoublePoints)
            if level == 6:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"MAXED", font = f"Constantia 20")  
            else:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"UPGRADE TO LVL {level} FOR {cost} COINS", font = f"Constantia 20")
            duration = getUpgrade("DOUBLE POINTS")//1000
            canvas.create_text(buttonCenter[0]+400, buttonCenter[1]-45, text = f"DURATION: {duration} SECONDS", font = f"Constantia 15")  



            buttonCenter = (self.cx/3, self.cy*(5/4))
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.upgradeMagnet)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.magnetImage))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "", font = f"Constantia 40") 
            level = (getUpgrade("MAGNET")-10000)//2000
            cost = int(getUpgrade("MAGNET")/75)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + 675, buttonCenter[1] + 20, fill = "seashell3", width = 4, onClick = self.upgradeMagnet)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + (675-150)/6 * level + 150, buttonCenter[1] + 20, width = 4, fill = "limegreen", onClick = self.upgradeMagnet)
            if level == 6:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"MAXED", font = f"Constantia 20")  
            else:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"UPGRADE TO LVL {level} FOR {cost} COINS", font = f"Constantia 20")
            duration = getUpgrade("MAGNET")//1000
            canvas.create_text(buttonCenter[0]+400, buttonCenter[1]-45, text = f"DURATION: {duration} SECONDS", font = f"Constantia 15")  

            buttonCenter = (self.cx/3, self.cy*(6.25/4))
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.upgradeAI)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.AIImage))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "", font = f"Constantia 40") 
            level = (getUpgrade("AI")-10000)//2000
            cost = int(getUpgrade("AI")/75)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + 675, buttonCenter[1] + 20, fill = "seashell3", width = 4, onClick = self.upgradeAI)
            canvas.create_rectangle(buttonCenter[0] + 150, buttonCenter[1] - 20, buttonCenter[0] + (675-150)/6 * level + 150, buttonCenter[1] + 20, width = 4, fill = "limegreen", onClick = self.upgradeAI)
            if level == 6:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"MAXED", font = f"Constantia 20")  
            else:
                canvas.create_text(buttonCenter[0]+400, buttonCenter[1], text = f"UPGRADE TO LVL {level} FOR {cost} COINS", font = f"Constantia 20")
            duration = getUpgrade("MAGNET")//1000
            canvas.create_text(buttonCenter[0]+400, buttonCenter[1]-45, text = f"DURATION: {duration} SECONDS", font = f"Constantia 15")   

            buttonCenter = (self.cx, self.cy*1.86)
            canvas.create_rectangle(buttonCenter[0] - 150, buttonCenter[1] - 75, buttonCenter[0] + 150, buttonCenter[1] + 75, fill = "", outline = "", onClick = self.toHome)
            canvas.create_image(buttonCenter, image = ImageTk.PhotoImage(self.button3))
            canvas.create_text(buttonCenter[0], buttonCenter[1]-7, text = "HOME", font = f"Constantia 40")   




        elif self.currentMode == "play":
            canvas.create_line(0,self.focus[1],self.width, self.focus[1])
            canvas.create_line(self.focus[0], 0, self.focus[0], self.width)


            canvas.create_rectangle(0, self.focus[1] - self.cameraPos[1], self.width, self.height, fill = "skyblue4", outline = "")
            if self.map == "MALIBU":
                canvas.create_rectangle(0,0,self.width, self.focus[1] - self.cameraPos[1], fill = "plum1", outline = "")
            else:
                canvas.create_rectangle(0,0,self.width, self.focus[1] - self.cameraPos[1], fill = "skyblue", outline = "")
            lanes, rails = self.createLanesAndRails()

            for lanes in lanes:
                lanes.render(canvas)

            for rails in rails:
                rails.render(canvas)

            for plank in self.planks:
                plank.render(canvas)


            for coin in self.coins:
                coin.render(canvas)

            renderOrder = [] #think reverse because what's rendered last is up front
            if self.runner.currentLane == 0:
                renderOrder = [4,3, 2,1,-2,-1,0]
            elif self.runner.currentLane == 1:
                renderOrder = [4,-2,3,-1,2,0,1]
            else:
                renderOrder = [-2,-1,0,4,1,3,2]

            newOrder = []
            
            for v in renderOrder:
                for obj in self.objects:
                    if obj.lane == v:
                        newOrder += [obj]

            for obj in newOrder:
                obj.render(canvas)

            self.runner.render(canvas)

            #display score
            textSize = self.height/40
            canvas.create_rectangle(0,0,self.width,45, fill = "black", outline = "")
            canvas.create_rectangle(0,self.height-45,self.width,self.height, fill = "black", outline = "")

            canvas.create_text(self.width/2, self.height-textSize, text = f"MAP: {self.map}", font = f"Arial {int(textSize)}", fill = "grey")

            canvas.create_text(self.width/2, textSize, text = f"{self.score}", font = f"Arial {int(textSize)}", fill = "white")

            #display coins
            canvas.create_text(self.width*.75, textSize, text = f"COINS: {self.coinsCollected}", font = f"Arial {int(textSize)}", fill = "yellow")
            displayMult = self.multiplier

            if self.runner.currentPowerUp == "DOUBLE POINTS":
                displayMult *= 2

            canvas.create_text(self.width*.25, textSize, text = f"x{displayMult}", font = f"Arial {int(textSize)}", fill = "cyan")

            #display powerup
            if self.runner.currentPowerUp != None and self.runner.powerUpTimeLeft > 0:
                canvas.create_rectangle(0,45,self.width,70, fill = "black", outline = "")
                canvas.create_rectangle(0,45,self.width*(self.runner.powerUpTimeLeft/getUpgrade(self.runner.currentPowerUp)),65, fill = "lime green", outline = "")
                canvas.create_text(self.width/2, 55, text = f"{self.runner.currentPowerUp}", font = f"Arial {15}", fill = "white")


        if self.transitioning == True:
            inc = math.sin(.5*math.pi*(self.transitionFrame/self.transitionFrames))*self.height/2
            canvas.create_rectangle(0,0,self.width, inc, fill = "black")
            canvas.create_rectangle(0,self.height-inc,self.width, self.height, fill = "black")


MetroMastersApp(width = 900, height = 900)
