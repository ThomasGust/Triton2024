import cv2
import numpy as np
import os
from tqdm import tqdm

def extract_frames(video_path, output_dir, step=1):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open the video file.")
    
    os.makedirs(output_dir, exist_ok=True)
    frame_count = 0
    saved_frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % step == 0:
            frame_filename = os.path.join(output_dir, f"frame_{saved_frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frame_count += 1
        frame_count += 1

    cap.release()
    print(f"Extracted {saved_frame_count} frames to {output_dir}")
    return output_dir

def feature_detection_and_matching(frame1, frame2):
    orb = cv2.ORB_create()
    
    kp1, des1 = orb.detectAndCompute(frame1, None)
    kp2, des2 = orb.detectAndCompute(frame2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    
    pts1 = np.array([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.array([kp2[m.trainIdx].pt for m in matches])
    
    return pts1, pts2, matches

def triangulate_points(K, pts1, pts2):
    E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, prob=0.999, threshold=1.0)
    _, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)
    
    #print(pts1)
    #pts1 = pts1[mask.ravel() == 1]
    #pts2 = pts2[mask.ravel() == 1]
    
    #pts1_h = cv2.convertPointsToHomogeneous(pts1)[:, 0, :]
    #pts2_h = cv2.convertPointsToHomogeneous(pts2)[:, 0, :]
    
    P1 = np.dot(K, np.hstack((np.eye(3), np.zeros((3, 1)))))
    P2 = np.dot(K, np.hstack((R, t)))
    
    points_4d_hom = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
    points_4d = points_4d_hom[:3] / points_4d_hom[3]
    
    return points_4d.T

def reconstruct_3d(video_path, frames_dir, K):
    extract_frames(video_path, frames_dir)
    
    frame_files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')])
    point_cloud = []
    
    for i in tqdm(range(len(frame_files) - 1), "Reconstructing 3D"):
        frame1 = cv2.imread(frame_files[i], cv2.IMREAD_GRAYSCALE)
        frame2 = cv2.imread(frame_files[i + 1], cv2.IMREAD_GRAYSCALE)
        
        pts1, pts2, matches = feature_detection_and_matching(frame1, frame2)
        points_3d = triangulate_points(K, pts1, pts2)
        
        point_cloud.extend(points_3d)
    
    point_cloud = np.array(point_cloud)
    return point_cloud

if __name__ == "__main__":
    video_path = 'C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\\video\data\photog_sample.mp4'
    frames_dir = 'C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\photogrammetry\extracted_frames'
    
    # Camera intrinsic parameters
    K = np.array([[1000, 0, 320],
                  [0, 1000, 240],
                  [0, 0, 1]], dtype=float)
    
    point_cloud = reconstruct_3d(video_path, frames_dir, K)
    
    # Save point cloud to a file
    np.save("point_cloud.npy", point_cloud)
    print("3D reconstruction completed and saved to point_cloud.npy")
