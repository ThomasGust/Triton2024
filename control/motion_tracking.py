import cv2
import numpy as np
import torch

width=1920
height= 1080
cam=cv2.VideoCapture(0,cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))
 
cv2.namedWindow('myTracker')
cv2.moveWindow('myTracker',width,0)
 
hueLow=10
hueHigh=20
satLow=10
satHigh=250
valLow=10
valHigh=250

p = torch.nn.MaxPool2d(2, 2)
while True:
    ignore,  frame = cam.read()

    frame_red = frame[:, :, 2]
    frame_red = np.expand_dims(np.expand_dims(frame_red, 0), -1)
    frame_red = p(torch.tensor(frame_red))

    print(frame_red.shape)
    cv2.imshow("frame", frame_red)
    if cv2.waitKey(1) & 0xff ==ord('q'):
        break