import os
import cv2


frames_dir = "photogrammetry/extracted_frames"
output_dir = "splits"

#Loop through extracted frames and take every 30th file
frames = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')])
os.makedirs(output_dir, exist_ok=True)
for i, frame in enumerate(frames[::50]):
    frame_name = os.path.basename(frame)
    frame_output_path = os.path.join(output_dir, frame_name)
    img = cv2.imread(frame)
    cv2.imwrite(frame_output_path, img)