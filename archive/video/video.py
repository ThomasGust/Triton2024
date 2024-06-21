import cv2
import os
import time

def video_to_frames(p, path_output_dir):
    # extract frames from a video and save to directory as 'x.png' where 
    # x is the frame index

    video = os.path.join("video\\data\\photogrammetry.mp4")
    vidcap = cv2.VideoCapture(video)
    count = 0
    print(vidcap)
    print(vidcap.isOpened())
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2.imwrite(os.path.join(path_output_dir, f"{count}.png"), image)
            count += 1
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()

video_to_frames('video\\data', 'video\\frames')
"""
img = cv2.imread("video\\frames\\510.png")
img = cv2.resize(img, [int(img.shape[1]/2), int(img.shape[0]/2)])
cv2.imwrite("reference.png", img)
cv2.imshow("mat", img)
cv2.waitKey(0)
"""