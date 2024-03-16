
import ImageHandler
import cv2
from PIL import Image, ImageDraw
import AStar
import Mesh
import numpy


def parseFile(fileName) :

    videoData = []
    frameData = []

    file = open(fileName, 'r')
    data = file.read().splitlines()
    file.close()

    for i in range(len(data)) :
        i = data[i]

        if i == 'new img' :
            videoData.append(frameData)
            frameData = []
            continue

        q = i.split()

        name = q[0]
        p = float(q[1])
        x1 = int(q[2])
        y1 = int(q[3])
        x2 = int(q[4])
        y2 = int(q[5])

        frameData.append(ImageHandler.Object(name, p, x1, y1, x2, y2))

    return videoData

if __name__ == '__main__' :

    videoData = parseFile('data.txt')

    cap = cv2.VideoCapture("video.avi")
    while not cap.isOpened():
        cap = cv2.VideoCapture("video.avi")
        cv2.waitKey(1000)
        print("Wait for the header")

    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    q = 0
    while True:
        flag, frame = cap.read()
        if flag:
            # The frame is ready and already captured

            frameData = videoData[q]

            for object in frameData :

                if object.p < 0.75 : continue

                font = cv2.FONT_HERSHEY_SIMPLEX
                org = (object.x1, object.y2)
                cv2.putText(frame, object.name, org, font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.rectangle(frame, (object.x1, object.y1), (object.x2, object.y2), color=(255, 0, 0), thickness=2)

            positionData = ImageHandler.calcDistanceAndAngle(frameData, None)

            AStar.IMAGE_SIZE_X = 1000
            AStar.IMAGE_SIZE_Y = 500
            AStar.POOL_SIZE_X = 50
            AStar.POOL_SIZE_Y = 25

            image = Image.new('RGB', (AStar.IMAGE_SIZE_X, AStar.IMAGE_SIZE_Y), AStar.BACKGROUND_COLOR)
            draw = ImageDraw.Draw(image)

            selfX = AStar.POOL_SIZE_X / 2
            selfY = 1

            AStar.AStar.drawCircle(draw, selfX, selfY, 0.6, AStar.CIRCLES_COLOR, AStar.CIRCLES_BORDER_COLOR,
                             AStar.CIRCLES_BORDER_WIDTH)

            for object in positionData:
                polarAngle = 90 - object[1]
                d = object[0]
                name = object[2]
                r = ImageHandler.sizes[name][2] / 5
                color =  ImageHandler.sizes[name][3]
                #print('r =', r)
                x = d * Mesh.cos(polarAngle) + selfX
                y = d * Mesh.sin(polarAngle) + selfY

                AStar.AStar.drawCircle(draw, x, y, r, color, AStar.CIRCLES_BORDER_COLOR,
                                       AStar.CIRCLES_BORDER_WIDTH)

            open_cv_image = numpy.array(image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()

            cv2.imshow('video2', open_cv_image)

            cv2.imshow('video', frame)
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            q += 1

            print(str(pos_frame) + " frames")
        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
            print("frame is not ready")
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1000)

        if cv2.waitKey(10) == 27:
            break
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            # If the number of captured frames is equal to the total number of frames,
            # we stop
            break
