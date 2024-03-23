import cv2
import numpy as np
import torch
import skimage.measure

width=1920
height= 1080
cam=cv2.VideoCapture(0,cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))

block_size = 16
while True:
    ignore,  frame = cam.read()

    frame_red = np.divide(frame[:, :, 2]^10, np.sum(frame, axis=-1))

    frame_red = skimage.measure.block_reduce(frame_red,block_size,np.max)
    frame_red = np.expand_dims(frame_red, -1)
    frame_red = cv2.resize(frame_red, (frame_red.shape[0]*block_size, frame_red.shape[1]*block_size))
    
    red_threshold = 0.5

    cv2.imshow("frame", frame_red)
    if cv2.waitKey(1) & 0xff ==ord('q'):
        break