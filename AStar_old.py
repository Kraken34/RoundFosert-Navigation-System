#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import random
import time
import math
import pickle


POINT_RADIUS = 2

IMAGE_SIZE_X = 5000
IMAGE_SIZE_Y = 2500

POOL_SIZE_X = 500
POOL_SIZE_Y = 250


class Circle:
    
    def __init__(self, x, y, r, name='UNDEFINED'):
        self.name = name
        self.x = x
        self.y = y
        self.r = r
        self.nodes = []
        self.antinodes = []
        self.saw = False


class Node:

    def __init__(self, x, y, circleIndex, polarAngle):

        self.x = x 
        self.y = y
        self.polarAngle = polarAngle
        self.f = 0
        self.g = 0
        self.h = 0
        self.previous = None
        self.path = None
        self.circleIndex = circleIndex
        self.pathLenth = 0
        self.saw = False

    def __str__(self) :
        return '[' + str(self.x) + ' ' + str(self.y) + ']'

        
class AStar:

    def __init__(self):
        pass

    @staticmethod
    def drawLine(draw, x1, y1, x2, y2, color='pink', width=1):
        if (draw == None): return
        # return
        draw.line((x1 * IMAGE_SIZE_X / POOL_SIZE_X, IMAGE_SIZE_Y - y1 * IMAGE_SIZE_Y / POOL_SIZE_Y,
                   x2 * IMAGE_SIZE_X / POOL_SIZE_X, IMAGE_SIZE_Y - y2 * IMAGE_SIZE_Y / POOL_SIZE_Y), color, width)

    @staticmethod
    def drawCircle(draw, x, y, r, color, outline='black', width=0):
        if (draw == None) : return
        # return
        x = x * IMAGE_SIZE_X / POOL_SIZE_X
        r = r * IMAGE_SIZE_X / POOL_SIZE_X
        y = y * IMAGE_SIZE_Y / POOL_SIZE_Y
        draw.ellipse((x - r, IMAGE_SIZE_Y - y - r, x + r, IMAGE_SIZE_Y - y + r), color, outline, width)

    @staticmethod
    def drawArc(draw, x, y, r, start, end, color, width=0):
        if (draw == None): return
        # return
        x = x * IMAGE_SIZE_X / POOL_SIZE_X
        r = r * IMAGE_SIZE_X / POOL_SIZE_X
        y = y * IMAGE_SIZE_Y / POOL_SIZE_Y
        draw.arc((x - r, IMAGE_SIZE_Y - y - r, x + r, IMAGE_SIZE_Y - y + r), start, end, color, width)

    @staticmethod
    def binFind(v, c):
        y, x = -1, len(v)
        
        while y + 1 != x:
            m = (x+y)//2
            if v[m] <= c : y = m
            else : x = m

        return y

    @staticmethod
    def clean_open_set(open_set, current_node):

        for i in range(len(open_set)):
            if open_set[i] == current_node:
                open_set.pop(i)
                break

        return open_set

    @staticmethod
    def checkLine(circles, x1, y1, x2, y2, circleIndexes, draw) :
        #x1, y1, x2, y2 = x2, y2, x1, y1

        #print('line:', x1, y1, '   ', x2, y2)
            
        for i in range(len(circles)) :
            if i in circleIndexes : continue
            circle = circles[i]
            
            #print('circle.x-y:', circle.x, circle.y)
            v1x = x2-x1
            v1y = y2-y1

            v2x = circle.x-x1
            v2y = circle.y-y1

            if (v1x**2 + v1y**2) == 0 :
                #AStar.drawCircle(draw, x1, y1, 2, 'orange')
                if ((x1-circle.x)**2 + (y1-circle.y)**2)**0.5 < circle.r : return False
                #else : return True
                else : continue
                
            u = (v1x*v2x + v1y*v2y)/(v1x**2 + v1y**2)
            u = max(min(1, u), 0)
                
            x = x1 + u*(x2 - x1)
            y = y1 + u*(y2 - y1)

            #AStar.drawCircle(draw, x, y, 2, 'blue')

            #print('u, x, y:', u, x, y)

            if ((circle.x - x)**2 + (circle.y - y)**2)**0.5 < circle.r : return False

        AStar.drawLine(draw, x1, y1, x2, y2)
        
        return True

    @staticmethod
    def getPolarAngle(x1, y1, x2, y2):
        x = x2-x1
        y = y2-y1
        
        angle = math.acos(x/(x**2 + y**2)**0.5)/2/math.pi*360

        if y < 0 : angle = 360 - angle

        return angle

    @staticmethod
    def getPolarAngle2(x1, y1, c):
        x = x1-c.x
        y = y1-c.y
        
        angle = math.acos(x/(x**2 + y**2)**0.5)/2/math.pi*360

        if y < 0 : angle = 360 - angle

        return angle

    @staticmethod
    def isPointInsideCircle(node, circle):
        return ((node.x-circle.x)**2 + (node.y-circle.y)**2)**0.5 <= circle.r
    
    @staticmethod
    def findNeighborsFromPoint(circles, node, draw, n=False, n2=False):

        neighbors = []
        x = node.x
        y = node.y

        #print("aaaa", x, y)
        #AStar.drawCircle(draw, x, y, 7, 'green', 'black', 1)
        #AStar.drawCircle(draw, 100, 100, 5.5, 'green', 'black', 1)
        #AStar.drawCircle(draw, 200, 100, 5.5, 'green', 'black', 1)
        #AStar.drawCircle(draw, 10, 10, 6.5, 'green', 'black', 1)

        for i in range(len(circles)) :
            circle = circles[i]
            
            #if AStar.isPointInsideCircle(node, circle) : continue
            #if circle.r <= 0 : continue


            if ((circle.x-x)**2 + (circle.y-y)**2)**0.5 < circle.r : return []

            x2 = (x + circle.x)/2
            y2 = (y + circle.y)/2
            r = ((x-x2)**2 + (y-y2)**2)**0.5
            d = r

            a = circle.r**2/2/d
            h = (circle.r**2 - a**2)**0.5

            x3 = circle.x + a/d*(x2-circle.x)
            y3 = circle.y + a/d*(y2-circle.y)

            x4 = x3 + h/d*(y2-circle.y)
            y4 = y3 - h/d*(x2-circle.x)

            x5 = x3 - h/d*(y2-circle.y)
            y5 = y3 + h/d*(x2-circle.x)

            #print('I = ', i)

            if AStar.checkLine(circles, x4, y4, x, y, [i], draw):
                node1 = Node(x4, y4, i, AStar.getPolarAngle2(x4, y4, circle))
                #print('AAAAAAAA:', x4, y4, circle.x, circle.y, i, AStar.getPolarAngle(x4, y4, circle.x, circle.y))
                node1.pathLenght = ((x-x4)**2 + (y-y4)**2)**0.5
                if n : node1.path = node
                neighbors.append(node1)
                if n2 : circle.nodes.append(node1)

            if AStar.checkLine(circles, x5, y5, x, y, [i], draw):
                node2 = Node(x5, y5, i, AStar.getPolarAngle2(x5, y5, circle))
                #print('AAAAAAAA:', x5, y5, i, AStar.getPolarAngle2(x5, y5, circle))
                node2.pathLenght = ((x-x5)**2 + (y-y5)**2)**0.5
                if n : node2.path = node
                neighbors.append(node2)
                if n2 : circle.nodes.append(node2)
        #print(len(neighbors))
        return neighbors

    @staticmethod
    def normalizeAngle(angle):
        if angle >= 0 : return angle % 360
        return 360 - ((-angle) % 360)

    @staticmethod
    def pointFromAngle(x, y, r, angle):
        x2 = x + r*math.cos(angle/360*2*math.pi)
        y2 = y + r*math.sin(angle/360*2*math.pi)
        return x2, y2

    @staticmethod
    def TwoCirclesIntersection(c1, c2):

        d = ((c1.x - c2.x)**2 + (c1.y - c2.y)**2)**0.5

        if d > c1.r + c2.r : return []
        if d < abs(c1.r - c2.r) : return []
        if d == 0 and c1.r == c2.r : return []

        a = (c1.r**2 - c2.r**2 + d**2)/2/d
        angle = math.acos(a/c1.r)/2/math.pi*360

        pa = AStar.getPolarAngle(c1.x, c1.y, c2.x, c2.y)

        #x1 = c1.x + c1.r*math.cos((pa-angle)/360*2*math.pi)
        #y1 = c1.y + c1.r*math.sin((pa-angle)/360*2*math.pi)
        #x2 = c1.x + c1.r*math.cos((pa+angle)/360*2*math.pi)
        #y2 = c1.y + c1.r*math.sin((pa+angle)/360*2*math.pi)
        #AStar.drawCircle(draw, x1, y1, 1, 'orange')

        return [AStar.normalizeAngle(pa-angle), AStar.normalizeAngle(pa+angle)]
        
    @staticmethod
    def findNeighborsForCircle(circles, circleIndex, draw):
        
        circle = circles[circleIndex]
        neighbors = []
        
        if circle.saw :
            n = []
            for i in circle.nodes :
                if i.saw == False : n.append(i)
            return n

        for i in range(len(circles)) :
            if i == circleIndex or circles[i].saw : continue
            
            c = circles[i]

            a1 = (circle.r + c.r) / ((circle.x-c.x)**2 + (circle.y-c.y)**2)**0.5
            if -1 <= a1 <= 1 :
                a1 = math.acos(a1)/2/math.pi*360

                #print(circle.x, circle.y, c.x, c.y)
                ap = AStar.getPolarAngle(circle.x, circle.y, c.x, c.y)

                x1 = circle.x + circle.r*math.cos((ap+a1)/360*2*math.pi)
                y1 = circle.y + circle.r*math.sin((ap+a1)/360*2*math.pi)

                x2 = circle.x + circle.r*math.cos((ap-a1)/360*2*math.pi)
                y2 = circle.y + circle.r*math.sin((ap-a1)/360*2*math.pi)

                x3 = c.x + c.r*math.cos((ap+a1+180)/360*2*math.pi)
                y3 = c.y + c.r*math.sin((ap+a1+180)/360*2*math.pi)

                x4 = c.x + c.r*math.cos((ap-a1+180)/360*2*math.pi)
                y4 = c.y + c.r*math.sin((ap-a1+180)/360*2*math.pi)

                if AStar.checkLine(circles, x1, y1, x3, y3, [i, circleIndex], draw):
                    node1 = Node(x1, y1, circleIndex, AStar.getPolarAngle2(x1, y1, circle))
                    node3 = Node(x3, y3, i, AStar.getPolarAngle2(x3, y3, c))
                    
                    node1.path = node3
                    node3.path = node1
                    
                    node1.pathLenght = ((x1-x3)**2 + (y1-y3)**2)**0.5
                    node3.pathLenght = node1.pathLenght
                    
                    neighbors.append(node1)
                    neighbors.append(node3)
                    circle.nodes.append(node1)
                    c.nodes.append(node3)

                    AStar.drawCircle(draw, x1, y1, 1, 'blue', 'black', 1)
                    AStar.drawCircle(draw, x3, y3, 1, 'blue', 'black', 1)

                if AStar.checkLine(circles, x2, y2, x4, y4, [i, circleIndex], draw):
                    node2 = Node(x2, y2, circleIndex, AStar.getPolarAngle2(x2, y2, circle))
                    node4 = Node(x4, y4, i, AStar.getPolarAngle2(x4, y4, c))
                    
                    node2.path = node4
                    node4.path = node2

                    node2.pathLenght = ((x2-x4)**2 + (y2-y4)**2)**0.5
                    node4.pathLenght = node2.pathLenght
                    
                    neighbors.append(node2)
                    neighbors.append(node4)
                    circle.nodes.append(node2)
                    c.nodes.append(node4)

                    AStar.drawCircle(draw, x2, y2, 1, 'blue', 'black', 1)
                    AStar.drawCircle(draw, x4, y4, 1, 'blue', 'black', 1)

            
            a2 = (circle.r - c.r) / ((circle.x-c.x)**2 + (circle.y-c.y)**2)**0.5
            
            if -1 <= a2 <= 1 :
                a2 = math.acos(a2)/2/math.pi*360

                #print(circle.x, circle.y, c.x, c.y)
                if circle.r > c.r :
                    ap = AStar.getPolarAngle(circle.x, circle.y, c.x, c.y)
                    #print('aaaB', circle.x, circle.y, c.x, c.y, ap)
                    #print(a2)
                else :
                    ap = AStar.getPolarAngle(c.x, c.y, circle.x, circle.y)
                    #print('aaaa', c.x, c.y, circle.x, circle.y, ap)
                    #print(a2)

                if a2 > 90 : a2 = 180 - a2

                #print(ap, a2)

                x5 = circle.x + circle.r*math.cos((ap+a2)/360*2*math.pi)
                y5 = circle.y + circle.r*math.sin((ap+a2)/360*2*math.pi)

                x6 = circle.x + circle.r*math.cos((ap-a2)/360*2*math.pi)
                y6 = circle.y + circle.r*math.sin((ap-a2)/360*2*math.pi)

                x7 = c.x + c.r*math.cos((ap+a2)/360*2*math.pi)
                y7 = c.y + c.r*math.sin((ap+a2)/360*2*math.pi)

                x8 = c.x + c.r*math.cos((ap-a2)/360*2*math.pi)
                y8 = c.y + c.r*math.sin((ap-a2)/360*2*math.pi)

                if AStar.checkLine(circles, x5, y5, x7, y7, [i, circleIndex], draw):
                    node5 = Node(x5, y5, circleIndex, AStar.getPolarAngle2(x5, y5, circle))
                    node7 = Node(x7, y7, i, AStar.getPolarAngle2(x7, y7, c))
                    
                    node5.path = node7
                    node7.path = node5

                    node5.pathLenght = ((x5-x7)**2 + (y5-y7)**2)**0.5
                    node7.pathLenght = node5.pathLenght
                    
                    neighbors.append(node5)
                    neighbors.append(node7)
                    circle.nodes.append(node5)
                    c.nodes.append(node7)

                    AStar.drawCircle(draw, x5, y5, 1, 'blue', 'black', 1)
                    AStar.drawCircle(draw, x7, y7, 1, 'blue', 'black', 1)

                if AStar.checkLine(circles, x6, y6, x8, y8, [i, circleIndex], draw):
                    node6 = Node(x6, y6, circleIndex, AStar.getPolarAngle2(x6, y6, circle))
                    node8 = Node(x8, y8, i, AStar.getPolarAngle2(x8, y8, c))
                    
                    node6.path = node8
                    node8.path = node6

                    node6.pathLenght = ((x6-x8)**2 + (y6-y8)**2)**0.5
                    node8.pathLenght = node6.pathLenght
                    
                    neighbors.append(node6)
                    neighbors.append(node8)
                    circle.nodes.append(node6)
                    c.nodes.append(node8)

                    AStar.drawCircle(draw, x6, y6, 1, 'blue', 'black', 1)
                    AStar.drawCircle(draw, x8, y8, 1, 'blue', 'black', 1)

        for c in circles :
            #if c.saw : continue
            circle.antinodes += AStar.TwoCirclesIntersection(circle, c)
        circle.antinodes.sort()

        circle.saw = True

        n = []
        for i in circle.nodes :
            if i.saw == False : n.append(i)
        return n
        #return circle.nodes

    @staticmethod
    def findNeighbors(circles, node, draw):
        #print('\nfindNeighbors')
        #if node.path == None :
            #print('from:', node.circleIndex, node.x, node.y, 'None')
        #else :
            #print('from:', node.circleIndex, node.x, node.y, node.path.circleIndex)
        #input()

        if node.circleIndex == None or node.circleIndex == -1 : return AStar.findNeighborsFromPoint(circles, node, draw, False, True)
        return AStar.findNeighborsForCircle(circles, node.circleIndex, draw)

    @staticmethod
    def hordD(circles, node1, node2):
        #print('\nhordD')
        
        if node1.circleIndex == None : return AStar.lineD(node1, node2)

        if node1.circleIndex != node2.circleIndex :
            print("Error: diferent circles in hordD!")
            return 0, 0
            #raise SystemExit
        
        c = circles[node1.circleIndex]
        r = c.r
        x, y = c.x, c.y

        l = 2*math.pi*r

        v1x = node1.x-x
        v1y = node1.y-y
        v2x = node2.x-x
        v2y = node2.y-y

        #print(v1x, v1y, v2x, v2y, (v1x*v2x + v1y*v2y)/(v1x**2 + v1y**2)**0.5/(v2x**2 + v2y**2)**0.5)
      
        a = math.acos(round((v1x*v2x + v1y*v2y)/(v1x**2 + v1y**2)**0.5/(v2x**2 + v2y**2)**0.5, 14))/2/math.pi*360

        antinodes = c.antinodes
        #print(node1.polarAngle, node2.polarAngle, antinodes)
        if antinodes :
            
            #AStar.drawCircle(draw, node1.x, node1.y, 3, 'orange')
            #AStar.drawCircle(draw, node2.x, node2.y, 3, 'orange')

            if node1.polarAngle > node2.polarAngle : node1, node2 = node2, node1

            a1 = node1.polarAngle
            a2 = node2.polarAngle

            #direction = -1 # against clock arrow

            #d1 = node1.polarAngle
            #d2 = node1.polarAngle + 180

            #if d2 < 360 :
            #    if d1 <= node2.polarAngle <= d2 : direction = 1
            #else :
            #    d2 = d2 % 360
            #    if d2 > node2.polarAngle or d1 < node2.polarAngle : direction = 1
            
            v1 = AStar.binFind(antinodes, node1.polarAngle)
            v2 = AStar.binFind(antinodes, node2.polarAngle)

            #a1 = node1.polarAngle
            #a2 = node2.polarAngle
            
            #if direction == 1 :
            #    if a1 > a2 :
            #        if v1 == len(antinodes)-1 and

            
            if v1 != v2 and (v2 != len(antinodes)-1 or v1 > 0) :
                #print(10**6)
                return 10**6, 0
            if v1 != v2 and a1 < a2 < a1+180 :
                #print('1:', 360 - a, a1 < a2 < a1+180)
                return l - a/360*l, 0
            if (v2 != len(antinodes)-1 or v1 > 0) and not a1 < a2 < a1+180 :
                #print('2:', 360 - a, a1 < a2 < a1+180)
                return l - a/360*l, 0

        #print('3:', a, a1 < a2 < a1+180)
        return a/360*l, 0

    @staticmethod
    def lineD(node1, node2):
        v1x = node1.x-node2.x
        v1y = node1.y-node2.y

        return (v1x**2 + v1y**2)**0.5
    
    @staticmethod
    def start_path(circles, open_set, current_node, end, draw):
        #print('\nstart_path')

        best_way = 0
        for i in range(len(open_set)):
            if open_set[i].f < open_set[best_way].f: best_way = i

        current_node = open_set[best_way]
        final_path = []

        #print('\nopenset len:', len(open_set))
        #for neighbor in open_set:
        #    print('\nnode.circleIndex =', neighbor.circleIndex, ' x, y:', neighbor.x, neighbor.y)
        #    print('ADR =', neighbor)
        #    print('neighbor.path =', neighbor.path)
        #    print('PREV =', neighbor.previous)
        #    print('G =', neighbor.g)
        #    print('H =', neighbor.h)
        #    print('F =', neighbor.f)

        #print('\nCurrent_node.circleIndex =', current_node.circleIndex, ' x, y:', current_node.x, current_node.y)
        #print('ADR =', current_node)
        #print('PREV =', current_node.previous)
        #print('G =', current_node.g)
        #print('H =', current_node.h)
        #print('F =', current_node.f)

        if current_node.circleIndex == -1: # == end
            temp = current_node
            q = 0
            while temp.previous:
                final_path.append(temp.previous)
                        
                AStar.drawCircle(draw, temp.x, temp.y, 1, 'yellow', 'black', 1)
                c = temp
                temp = temp.previous
                if q % 2 == 0 : AStar.drawLine(draw, c.x, c.y, temp.x, temp.y, 'green', 7)
                else :
                    angle1 = 360 - AStar.getPolarAngle(circles[c.circleIndex].x, circles[c.circleIndex].y, c.x, c.y)
                    angle2 = 360 - AStar.getPolarAngle(circles[c.circleIndex].x, circles[c.circleIndex].y, temp.x, temp.y)

                    if angle2 < angle1 :
                        angle2, angle1 = angle1, angle2
                    
                    AStar.drawArc(draw, circles[c.circleIndex].x, circles[c.circleIndex].y, circles[c.circleIndex].r, angle1, angle2, 'green', 7)
                    
                    
                q += 1
            return open_set, current_node, final_path

        open_set = AStar.clean_open_set(open_set, current_node)
        current_node.saw = True

        
        neighbors = AStar.findNeighbors(circles, current_node, draw)
        #AStar.drawCircle(draw, current_node.x, current_node.y, 5.5, 'pink', 'black', 1)
        AStar.drawCircle(draw, current_node.x, current_node.y, 1.5, 'red', 'black', 1)

        #print('\nneighbors len:', len(neighbors))
        #for neighbor in neighbors:
        #    print('\nneighbor.circleIndex =', neighbor.circleIndex, ' x, y:', neighbor.x, neighbor.y)
        #    print('ADR =', neighbor)
        #    print('neighbor.path =', neighbor.path)
        #    print('PREV =', neighbor.previous)
        #    print('SAW =', neighbor.saw)
        #    print('G =', neighbor.g)
        #    print('H =', neighbor.h)
        #    print('F =', neighbor.f)
        
        for neighbor in neighbors:

            if current_node.circleIndex == None :
                if neighbor.saw == True : continue
                else:
                    temp_g = current_node.g + AStar.lineD(current_node, neighbor)
                    neighbor.g = temp_g
                    neighbor.h = AStar.lineD(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.previous = current_node

                    if neighbor not in open_set :
                        open_set.append(neighbor)
            else :

                if neighbor.saw == True : continue
                else:
                    if neighbor.path == None : continue
                    temp_g = current_node.g + AStar.hordD(circles, current_node, neighbor)[0]

                    #if AStar.hordD(circles, current_node, neighbor)[1] == -1 :
                    #    print('\nCurrent_node.circleIndex =', current_node.circleIndex, ' x, y:', current_node.x, current_node.y)
                    #    print('ADR =', current_node)
                    #    print('PREV =', current_node.previous)
                    #    print('G =', current_node.g)
                    #    print('H =', current_node.h)
                    #    print('F =', current_node.f)
                    #    
                    #    print('\nneighbors len:', len(neighbors))
                    #    for neighbor in neighbors:
                    #        print('\nneighbor.circleIndex =', neighbor.circleIndex, ' x, y:', neighbor.x, neighbor.y)
                    #        print('ADR =', neighbor)
                    #        print('neighbor.path =', neighbor.path)
                    #        print('PREV =', neighbor.previous)
                    #        print('SAW =', neighbor.saw)
                    #        print('G =', neighbor.g)
                    #        print('H =', neighbor.h)
                    #        print('F =', neighbor.f)
                    
                    if neighbor.g < temp_g and neighbor.g != 0 : continue
                    
                    neighbor.g = temp_g
                    neighbor.h = AStar.lineD(neighbor, neighbor.path) + AStar.lineD(neighbor.path, end)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.previous = current_node

                    #if neighbor.path not in open_set and ((neighbor.path.g > neighbor.g + AStar.lineD(neighbor, neighbor.path) or neighbor.path.g == 0)) :
                    if (neighbor.path.g > neighbor.g + AStar.lineD(neighbor, neighbor.path) or neighbor.path.g == 0) :
                        
                        neighbor.path.previous = neighbor
                        neighbor.path.g = neighbor.g + AStar.lineD(neighbor, neighbor.path)
                        neighbor.path.h = AStar.lineD(neighbor.path, end)
                        neighbor.path.f = neighbor.path.g + neighbor.path.h
                        
                        open_set.append(neighbor.path)

        #print('\nneighbors len:', len(neighbors))
        #for neighbor in neighbors:
        #    print('\nneighbor.circleIndex =', neighbor.circleIndex, ' x, y:', neighbor.x, neighbor.y)
        #    print('ADR =', neighbor)
        #    print('neighbor.path =', neighbor.path)
        #    print('PREV =', neighbor.previous)
        #    print('SAW =', neighbor.saw)
        #    print('G =', neighbor.g)
        #    print('H =', neighbor.h)
        #    print('F =', neighbor.f)

        return open_set, current_node, final_path

    def main(self, start, end, circles, needToDrive, needToDrawAllLines):

        self.start = start
        self.end = end
        self.circles = []

        im, draw = None, None
        if needToDrive:
            im = Image.new('RGB', (IMAGE_SIZE_X, IMAGE_SIZE_Y), (0, 0, 0))
            draw = ImageDraw.Draw(im)

        endNode = Node(end[0], end[1], 0, 0)
        startNode = Node(start[0], start[1], 0, 0)
        for circle in circles :
            if circle[2] > 0 : # circle.r
                if AStar.isPointInsideCircle(endNode, Circle(circle[0], circle[1], circle[2])) or  \
                   AStar.isPointInsideCircle(startNode, Circle(circle[0], circle[1], circle[2]))  :
                    #AStar.drawCircle(draw, circle.x, circle.y, circle.r, '#202020', 'black', 1)
                    AStar.drawCircle(draw, circle[0], circle[1], circle[2], '#202020', 'black', 1)
                    continue
                self.circles.append(Circle(circle[0], circle[1], circle[2]))

        for circle in self.circles :
            AStar.drawCircle(draw, circle.x, circle.y, circle.r, 'white', 'black', 1)
            
        AStar.drawCircle(draw, start[0], start[1], POINT_RADIUS, '#618ab2')
        AStar.drawCircle(draw, end[0], end[1], POINT_RADIUS, '#618ab2')

        startNode = Node(start[0], start[1], None, 0)
        endNode = Node(end[0], end[1], -1, 0)
        n1 = AStar.findNeighborsFromPoint(self.circles, startNode, draw)
        n2 = AStar.findNeighborsFromPoint(self.circles, endNode, draw, True, True)

        #if not n1 : return 2, [], None
        #if not n2 : return 1, [], None

        for i in n1 : AStar.drawCircle(draw, i.x, i.y, 1, 'blue')
        for i in n2 : AStar.drawCircle(draw, i.x, i.y, 1, 'blue')

        if needToDrawAllLines :
            for i in range(len(self.circles)) : AStar.findNeighborsForCircle(self.circles, i, draw)
        

        open_set  = []
        #closed_set  = []
        current_node = None
        final_path  = []
        open_set.append(startNode)
        self.end = endNode

        #im.show()
        
        while len(open_set) > 0:
            open_set, current_node, final_path = AStar.start_path(self.circles, open_set, current_node, endNode, draw)
            if len(final_path) > 0: break
        AStar.drawCircle(draw, startNode.x, startNode.y, 1, 'yellow', 'black', 1)

        return final_path, im



if __name__ == "__main__":

    a_star = AStar()

    startPoint = [10, 10]
    endPoint = [490, 249]


    circles = []
    for i in range(60) :
        circles.append([random.randint(0, 499), random.randint(0, 249), random.randint(1, 40)])

    time1 = time.time()
    final_path, im = a_star.main(startPoint, endPoint, circles, False, False)
    print("Time to make a path and draw:", time.time() - time1)

    time1 = time.time()
    final_path, im = a_star.main(startPoint, endPoint, circles, False, True)
    print("Time to make a path and draw:", time.time() - time1)

    time1 = time.time()
    final_path, im = a_star.main(startPoint, endPoint, circles, True, False)
    print("Time to make a path and draw:", time.time()-time1)
    im.show()
    im.save('draw-arc.png')

    time1 = time.time()
    final_path, im = a_star.main(startPoint, endPoint, circles, True, True)
    print("Time to make a path and draw:", time.time() - time1)
    im.show()
    im.save('draw-arc2.png')
        

 


