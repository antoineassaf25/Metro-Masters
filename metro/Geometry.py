"""
    This file handles all of mathematical geometry in a 2.5D field, 
    containing classes of fundamental geometry including:
        --> Point
        --> Line
        --> Surface
        --> Rectangluar Prism
        --> Focused Point
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



#2.5D Geometry class/subclasses (self-written)
class Geometry():
    def __init__(self, app, points, color = "grey"):
        self.app = app
        self.points = points
        self.color = color

class Point(Geometry):
    def __init__(self, app, x, y, z, color = "black", h = 0):
        super().__init__(app, None, color)
        self.x = x
        self.y = y
        self.z = z
        self.zOffset = z * 10
        self.r = 2
        self.h = h
    
    def coordinatesToAbsolute(self):
        distanceFromFocusX = self.app.focus[0] - self.x * self.app.width
        distanceFromFocusY = self.app.focus[1] - self.y * self.app.height
        distanceFromFocus = distance(self.x, self.y, self.app.focus[0], self.app.focus[1])
        ratio = self.z

        newX =  self.x * self.app.width + distanceFromFocusX*ratio
        newY =  self.y * self.app.height + distanceFromFocusY*ratio
        heightChange = self.h*self.app.height * (1-self.z)

        return newX - self.app.cameraPos[0], newY - heightChange - self.app.cameraPos[1]

    def changeDistance(self, scrollZ):
        self.z = -2**(-(scrollZ + self.zOffset)) + 1

    def render(self, canvas):
        x, y = self.coordinatesToAbsolute()
        canvas.create_oval(x-self.r, y-self.r,x+self.r,y+self.r, fill = self.color)

class Line(Geometry):
    def render(self, canvas):
        canvas.create_line(self.points[0].coordinatesToAbsolute(),self.points[1].coordinatesToAbsolute(), fill = self.color)

class FocusedCircle(Point):
    def __init__(self, app, x, y, z, theText, size, color = "black", h = 0, speed = 0):
        super().__init__(app, x, y, z, color, h)
        self.size = size
        self.scale = size
        self.theText = theText
        self.speed = 0
        self.h = h
        self.color = color
        self.visible = False
        self.r = size

    def changeDistance(self, scrollZ):
        self.zOffset += scrollZ - self.speed
        self.z = -2**(-(scrollZ + self.zOffset)) + 1

    def render(self, canvas):
        if self.visible:
            x, y = self.coordinatesToAbsolute()
            r = self.r * (1-self.z)*10

            checkColor = self.color

            if self.app.runner.currentPowerUp == "MAGNET":
                checkColor = random.choice(["red", "white"])

            canvas.create_oval(x-r, y-r, x+r, y+r, fill = checkColor, width = r*.25)
                
            if r > 1:
                canvas.create_text(x,y, text = self.theText, font = f"Ariel {int(r)}")
    
class Surface(Geometry):

    def __len__(self):
        return len(self.points)

    def render(self,canvas):
        absolutePoints = []
        for point in self.points:
            absolutePoints += [(point.coordinatesToAbsolute())]
        canvas.create_polygon(absolutePoints, fill = self.color)

class rectPrism(Geometry):
    def __init__(self, app, surfaces, zDistance, h, speed = 0, cap = True):
        self.app = app
        self.cap = cap
        self.surfaces = surfaces
        self.speed = speed
        self.moving = True
        self.zDistance = zDistance
        self.h = h #+ surfaces[0].points[0].h
        self.extrudedSurfaces = []
        self.visible = False #turns true after position is calculated

        if h > 0:
            for surface in surfaces:
                for i in range(0, len(surface)):
                    point1 = surface.points[i]
                    nextI = i+1
                    if nextI == len(surface):
                        nextI = 0
                    point2 = surface.points[nextI]

                    point3 = Point(app, point2.x, point2.y, point2.z, point2.color, h) #point with height
                    point4 = Point(app, point1.x, point1.y, point1.z, point1.color, h) #point with height

                    wallSurface = Surface(app, [point1, point2, point3, point4], surface.color + "3")# str(2 + i%2))
                    self.extrudedSurfaces += [wallSurface]
            if self.cap:
                for surface in surfaces:
                    capPoints = []
                    for point in surface.points:
                        capPoints += [Point(app, point.x, point.y, point.z, point.color, h)]
                    capSurface = Surface(app, capPoints, surface.color + "4")
                    self.extrudedSurfaces += [capSurface]

    def changeDistance(self, scrollZ):
        self.zDistance += scrollZ - self.speed
        if self.moving:
            for surface in self.surfaces:
                for point in surface.points:
                    point.changeDistance(self.zDistance)
            for surface in self.extrudedSurfaces:
                for point in surface.points:
                    point.changeDistance(self.zDistance)

    def render(self, canvas):
        if self.visible:
            for surface in self.surfaces:
                surface.render(canvas)
            for extrudedSurface in self.extrudedSurfaces:
                extrudedSurface.render(canvas)

class Train(rectPrism):
    def __init__(self, app, surfaces, zDistance, h, lane, speed = 0, moving = True):
        super().__init__(app, surfaces, zDistance, h, speed, moving)
        self.lane = lane

class Decoration(rectPrism):
    def __init__(self, app, surfaces, zDistance, h, lane, speed = 0, moving = True):
        super().__init__(app, surfaces, zDistance, h, speed, moving)
        self.lane = lane

class JumpBarrier(rectPrism):
    def __init__(self, app, surfaces, zDistance, h, lane, speed = 0, moving = True):
        super().__init__(app, surfaces, zDistance, h, speed, moving)
        self.lane = lane

class DuckBarrier(rectPrism):
    def __init__(self, app, surfaces, zDistance, h, lane, speed = 0, moving = True):
        super().__init__(app, surfaces, zDistance, h, speed, moving)
        self.lane = lane

class Ladder(rectPrism):
    def __init__(self, app, surfaces, zDistance, h, lane, speed = 0, moving = True):
        super().__init__(app, surfaces, zDistance, h, speed, moving)
        self.lane = lane