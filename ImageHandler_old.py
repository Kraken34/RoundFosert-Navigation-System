
import math
import Mesh

PIXEL_RESOLUTION_X = 640
PIXEL_RESOLUTION_Y = 480

ANGLE_RESOLUTION_X = 60
ANGLE_RESOLUTION_Y = ANGLE_RESOLUTION_X * (PIXEL_RESOLUTION_Y / PIXEL_RESOLUTION_X)

MIN_P_VALUE = 0.75

UNIT_PER_ = 1/40

# размер в плитках, одна плитка = 1/3 метра
sizes = {
    'gate' : [1.5, 1.5, 4, 'blue'],
    'yellow_flare' : [0.15*2, 1.5, 1.5, 'yellow'],
    'red_flare' : [0.15*2, 1.5, 1.5, 'red'],
    #'red_bowl' : [0.13, 0.13, 0.8, 'red'],
    'blue_bowl' : [0.7, 0.13, 0.8, 'blue'],
    'red_bowl' : [0.7, 0.13, 0.8, 'red']
}

def tg(x) :
    return math.tan(x/360*2*math.pi)

def calcDistance(angleSize, realSize) :
    return realSize / (2 * tg(angleSize / 2))
    #return realSize / (1 * tg(angleSize / 1))
    #return realSize / Mesh.sin(angleSize)
    angleSize = 45
    #return realSize / angleSize
    return realSize / (2 * tg(angleSize / 1))

class Object :

    def __init__(self, name, p=0.0, x1=0, y1=0, x2=0, y2=0):
        self.name = name
        self.p = p
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return self.name + '->' + str(round(self.p, 2))

    def __repr__(self):
        return str(self)

def calcDistanceAndAngle(frameData, image) :

    objectPosition = []

    for object in frameData :

        if sizes.get(object.name, None) == None : continue

        #rint('adasd')
        #print(frameData)
        #input()

        if object.p < MIN_P_VALUE : continue

        name = object.name
        realSizeX, realSizeY = sizes[object.name][0], sizes[object.name][1]

        pixelSizeX = object.x2 - object.x1
        pixelSizeY = object.y2 - object.y1
        sizeX = pixelSizeX / PIXEL_RESOLUTION_X
        sizeY = pixelSizeY / PIXEL_RESOLUTION_Y
        angleSizeX = sizeX * ANGLE_RESOLUTION_X
        angleSizeY = sizeY * ANGLE_RESOLUTION_Y

        DX = calcDistance(angleSizeX, realSizeX)
        DY = calcDistance(angleSizeY, realSizeY)

        positionX = object.x1 + (object.x2 - object.x1) / 2
        angleX = (positionX / PIXEL_RESOLUTION_X) * ANGLE_RESOLUTION_X
        angle = angleX - ANGLE_RESOLUTION_X / 2

        objectPosition.append([DX, angle, name])

    # расстояние до объекта (в метрах)
    #distance = 15
    # угол до объекта (относительно "линни прямо" в правую сторону в градусах)
    #relativeAngle = -20 # влево на 20 градусов
    # название объекта
    #name = 'Врата'

    #return [[distance, relativeAngle, name]]
    #print(objectPosition)

    return objectPosition