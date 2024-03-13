import cv2


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

while True:
    ignore,  frame = cam.read()
    print(frame.shape)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xff ==ord('q'):
        break