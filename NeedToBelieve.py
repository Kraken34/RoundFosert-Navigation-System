
import ImageHandler
import Mesh

POOL_TARGET_DEEP = 25
FRAME_COUNT_TO_INACTIVE = 10

LOG_SAVE = False
LOG_SAVE_FILENAME = 'NTB_log.txt'

SELF_RADIUS = 0.8

DEFAULT_OBJECT_RADIUS = 2
# objectRadius = {'Врата' : 10,
#                 'Синий столб' : 5,
#                 'Зелёный столб' : 5,
#                 'Красный столб' : 5,
#                 'Жёлтый столб' : 5,
#                 'Ковёр с вёдрами' : 20}

class Vector :

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __abs__(self):
        return (self.x**2 + self.y**2 + self.x**2)**0.5

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'


class Object :

    def __init__(self, name) :
        self.name = name
        #self.pos = Vector(0, 0, 0)
        self.x = 0
        self.y = 0
        self.z = POOL_TARGET_DEEP
        self.isActive = False
        self.frameCount = 0

    def __str__(self):
        return '[' + str(self.x) + ', ' + str(self.y) + '] (' + str(self.isActive) + ')'

    def __repr__(self):
        return str(self)


def weightValue(a, b, value) :
    if value < -1: value = -1
    if value > 1 : value = 1

    if b < a :
        a, b = b, a
        value = 1 - value

    return a + (b - a) * value

class Map :

    def __init__(self, position, angle) :
        self.objects = dict()
        self.x = position[0]
        self.y = position[1]
        self.z = position[2]
        self.angle = angle
        self.frameCount = 0

    def updatePosition(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def updateObject(self, objectList) :

        print(self.objects)

        self.frameCount += 1

        for obj in objectList :
            #distance, relativeAngle, name
            self.__updateObject(obj[0], obj[1], obj[2])

        for obj in self.objects :
            obj = self.objects[obj]
            if obj.frameCount + FRAME_COUNT_TO_INACTIVE < self.frameCount :
                obj.isActive = False

    def __updateObject(self, distance, relativeAngle, name) :

        if name not in self.objects : self.objects[name] = Object(name)

        polarAngle = self.angle[2] - relativeAngle
        #self.objects[name].x = self.x + distance * Mesh.cos(polarAngle)
        #self.objects[name].y = self.y + distance * Mesh.sin(polarAngle)
        value = 0.3 + (self.frameCount-1 - self.objects[name].frameCount)/5
        self.objects[name].x = (weightValue(self.objects[name].x, self.x + distance * Mesh.cos(polarAngle), value))
        self.objects[name].y = (weightValue(self.objects[name].y, self.y + distance * Mesh.sin(polarAngle), value))

        self.objects[name].frameCount = self.frameCount
        self.objects[name].isActive = True

    @staticmethod
    def calcObjectRadius(obj) :
        #print(ImageHandler.objectData.get(obj.name, DEFAULT_OBJECT_RADIUS)[2] + SELF_RADIUS)
        return ImageHandler.objectData.get(obj.name, DEFAULT_OBJECT_RADIUS)[2] + SELF_RADIUS

    def find(self):
        return [self.x, self.y, 0]

    def calcPath(self, targetName) :

        circles = []
        for obj in self.objects :
            obj = self.objects[obj]
            if obj.isActive and obj.name != targetName :
                circles.append([obj.x, obj.y, Map.calcObjectRadius(obj)])

        startPoint = [self.x, self.y, self.z]

        if targetName not in self.objects or not self.objects[targetName].isActive:
            endPoint = self.find()
        else :
            endPoint = [self.objects[targetName].x, self.objects[targetName].y, self.objects[targetName].z]

        state, vector, image = Mesh.calcMove(circles, startPoint, self.angle, endPoint, True, POOL_TARGET_DEEP)
        if targetName not in self.objects and state == Mesh.STATE_OK : state = Mesh.STATE_FIND

        return state, vector, image

def sendVector(vector) :
    pass

def updateImage(map, data, image, targetName) :
    objectData = ImageHandler.calcDistanceAndAngle(data, image)

    if LOG_SAVE :
        file = open(LOG_SAVE_FILENAME, 'a')
        file.write('#imageData#' + str(data) + '\n')
        file.write('#objectData#' + str(objectData) + '\n')
        file.close()

    map.updateObject(objectData)

    state, vector = map.calcPath(targetName)

    if state != Mesh.STATE_ERROR and state != Mesh.STATE_COMPLETE : sendVector(vector)

    return state

def updatePosition(map, newPosition, targetName) :
    map.updatePosition(newPosition[0], newPosition[1], newPosition[2])