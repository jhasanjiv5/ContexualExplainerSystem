import cv2
import datetime
import numpy as np
scheme = '127.0.0.1'


def videoStream():
    host = scheme
    cap = cv2.VideoCapture('https://interactions.ics.unisg.ch/61-402/live-stream@'+host+':8080/web/admin.html')
    count = 0
    # while count < 20:
    ret, frame = cap.read()
    #     cv2.imwrite('frames/frame{}.jpg'.format(datetime.datetime.now()), frame)
    #
    #     count += 1
    cv2.destroyAllWindows()
    return frame