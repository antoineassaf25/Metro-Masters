"""
    This file handles the runners attributes, mainly including its own
        --> personal collision pointer
        --> current lane
        --> current powerup
        --> Jumping/Ducking/Falling anim/state
"""

# from https://www.diderot.one/course/34/chapters/2808/#anchor-segment-214904
from cmu_112_graphics import * #ModalApp, App, Mode

#from built-in functions into Python 3.85
import copy
import math
import random

#from @B2-1-33 www.diderot.one/course/34/chapters/2605/#anchor-atom-186051
def distance(x0, y0, x1, y1):
    return math.sqrt((x0 - y0)**2 + (x1 - y1)**2)

#from @B0-1-56 www.diderot.one/course/34/chapters/2288/#anchor-atom-188353 
def almostEqual(d1, d2, epsilon=10**-7):
    return (abs(d2 - d1) < epsilon)



class Runner():
    def __init__(self, app, color, currentLane = 1):
        self.app = app
        self.color = color
        self.currentLane = currentLane
        self.alive = True
        self.fLevel = 0
        self.j = 0 #jump height
        self.jumpPower = self.maxJumpPower = 30
        self.jumping = self.ducking = self.climbing = False
        self.switchingLanes = self.switchingLaneTime = 0 #will indicate which direction for animation
        self.r = 55
        self.forceField = False
        self.currentPowerUp = None
        self.powerUpTimeLeft = 0
        self.falling = False

        #this essentially locates where the player is. There are 18 "locations" a player can be in
        #for each lane
            #there is are two levels (on ground or on train)
                #A player can be either running, ducking, or jumping
        self.collisionBox = [
            [[False, False, False],[False, False, False]], 
            [[False, True, False],[False, False, False]],
            [[False, False, False],[False, False, False]]]

    def updateCollisionBox(self):
        for lane in range(3):
            if lane != self.currentLane: #if you are not in the lane, make sure the whole lane is falsified
                for j in range(2):
                    for k in range(3):
                        self.collisionBox[lane][j][k] = False
            else: #correct lane
                for j in range(2): #falsify everything first
                    for k in range(3):
                        self.collisionBox[lane][j][k] = False
                if self.jumping:
                    self.collisionBox[lane][self.fLevel][2] = True
                elif self.ducking:
                    self.collisionBox[lane][self.fLevel][0] = True
                else:
                    self.collisionBox[lane][self.fLevel][1] = True

    def changeLane(self, dLane):

        self.currentLane += dLane
        if not (0 <= self.currentLane < 3): #num lanes
            self.currentLane -= dLane
            return False
        
        self.updateCollisionBox()
        return True

    def jumpTick(self):
        
        self.j += self.jumpPower
        self.app.focus[1] += self.jumpPower #cameraAniamtion
        self.jumpPower += self.app.gravity
        

        if self.j < -self.jumpPower or almostEqual(self.jumpPower, -self.maxJumpPower):
            self.j = 0
            self.jumpPower = self.maxJumpPower
            self.jumping = False

        self.updateCollisionBox()

    def duckTick(self):
        
        self.app.focus[1] -= self.jumpPower/2 #cameraAniamtion
        self.jumpPower += self.app.gravity
        self.j -= self.jumpPower/2.5
        
        if almostEqual(self.jumpPower, -self.maxJumpPower):
            self.jumpPower = self.maxJumpPower
            self.ducking = False
            self.j = 0

        self.updateCollisionBox()

    def climbTick(self):
        #self.app.focus[1] = self.app.height/2
        if self.fLevel != 1:
            self.fLevel = 1
        self.app.cameraPos[1] -= 80
        if self.app.cameraPos[1] <= -(self.app.height * self.app.levelHeight):
            self.app.cameraPos[1] = -(self.app.height * self.app.levelHeight)
            self.climbing = False
            if self.fLevel == 0:
                self.j = 0
                self.jumpPower = self.maxJumpPower
                self.jumping = False

        self.updateCollisionBox()

    def checkFall(self):
        if self.falling or (self.fLevel == 1 and self.app.collisionBox[self.currentLane][0] != [True, True, True] and self.jumping == False): #no train below and not jumping
            self.falling = True
            if True: #instant as of right now
                self.fLevel = 0
                self.app.cameraPos[1] += 60
                if self.app.cameraPos[1] > 0:
                    self.app.cameraPos[1] = 0
                    self.falling = False

        self.updateCollisionBox()               

    def coordinatesToAbsolute(self):
        return self.app.width/2, self.app.height - 2*self.r - self.j

    def render(self, canvas):
        color = "black"
        if self.currentPowerUp == "SPEEDY BOOTS":
            color = random.choice(["limegreen", "white"])
        if self.currentPowerUp == "MAGNET":
            color = random.choice(["red", "white"]) 
        if self.currentPowerUp == "DOUBLE POINTS":
            color = random.choice(["cyan", "white"])  
        if self.currentPowerUp == "AI":
            color = random.choice(["pink", "white"])  
        canvas.create_oval(self.app.width/2 - self.r, self.app.height - 3*self.r - self.j, self.app.width/2+self.r, self.app.height-self.r - self.j, fill = color, width = 3)