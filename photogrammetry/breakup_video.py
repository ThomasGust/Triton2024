import os
import cv2
import shutil

VIDEO_PATH = "C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\photogrammetry\\video"
MESHROOM_INPUT_PATH = "C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\photogrammetry\\meshroom_input"
DESIRED_FRAMES = 30

if __name__ == "__main__":
    video_names = os.listdir(VIDEO_PATH)
    date2video = {int(name.split(".mp4")[0].replace("-", "").replace("_","").replace(".","")):name for name in video_names}

    highest_key = max(list(date2video.keys()))
    most_recent_video_name = date2video[highest_key]

    most_recent_video_path = os.path.join(VIDEO_PATH, most_recent_video_name)

    #Flush MESHROOM_INPUT_PATH directory
    shutil.rmtree(MESHROOM_INPUT_PATH)
    os.mkdir(MESHROOM_INPUT_PATH)

    vidcap = cv2.VideoCapture(most_recent_video_path)
    video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    #Given the video length and the desired frames, we can compute the frame modulus term
    
    mod_by = int(video_length/DESIRED_FRAMES)
    count = 0

    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            if count % mod_by == 0:
                cv2.imwrite(os.path.join(MESHROOM_INPUT_PATH, f"{count}.png"), image)
            count += 1
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()




