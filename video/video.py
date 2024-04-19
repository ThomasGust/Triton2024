import cv2
import os
import time

def video_to_frames(video, path_output_dir):
    # extract frames from a video and save to directory as 'x.png' where 
    # x is the frame index
    vidcap = cv2.VideoCapture(video)
    count = 0
    print(vidcap)
    print(vidcap.isOpened())
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            if count % 10 == 0:
                #image = cv2.rectangle(image, (650, 1080), (1200, 500), color=(0, 0, 0), thickness=-1)
                cv2.imwrite(os.path.join(path_output_dir, f"{count}.png"), image)
            count += 1
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()

video_to_frames('video\\data\\coral_vid.mkv', 'video\\frames')
"""
img = cv2.imread("video\\frames\\510.png")
img = cv2.resize(img, [int(img.shape[1]/2), int(img.shape[0]/2)])
cv2.imwrite("reference.png", img)
cv2.imshow("mat", img)
cv2.waitKey(0)
"""