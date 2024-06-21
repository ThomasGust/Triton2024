import torch
import torchvision.transforms as T
from PIL import Image
import glob
import os
import cv2
import numpy as np
import open3d as o3d
from tqdm import tqdm
device = torch.device("cuda")

def extract_frames(video_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in tqdm(range(frame_count), "Extracting frames"):
        ret, frame = cap.read()
        if not ret:
            break

        #print(frame.shape)
        height, width, _ = frame.shape[:3]

        # Calculate the new height after cropping out the top 20%
        new_height = int(height * 0.8)

        # Crop the image
        cropped_image = frame[height - new_height:height, 0:width]
        frame_path = os.path.join(output_dir, f'frame_{i:04d}.jpg')
        cv2.imwrite(frame_path, cropped_image)

    cap.release()

# Usage
video_path = 'C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\\video\data\photog_sample.mp4'
output_dir = 'C:\\Users\Thomas\OneDrive\Apps\Documents\GitHub\Triton\photogrammetry\extracted_frames'
extract_frames(video_path, output_dir)


# Load MiDaS model
model_type = "DPT_Large"  # MiDaS model type
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas = midas.to(device)

# Load transforms to resize and normalize the image for MiDaS
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

def estimate_depth(image_path, output_path):
    img = Image.open(image_path).convert('RGB')
    img_input = transform(np.array(img)).unsqueeze(0)

    with torch.no_grad():
        # Collapse first dimension
        img_input = img_input.squeeze(0).to(device)
        prediction = midas(img_input)

    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=img.size[::-1],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

    # Save depth map
    depth_map = prediction.cpu().numpy()
    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())  # Normalize to [0, 1]
    depth_map = (depth_map * 255).astype("uint8")

    depth_image = Image.fromarray(depth_map)
    depth_image.save(output_path)

# Process all extracted frames
frames = glob.glob(os.path.join(output_dir, "*.jpg"))
depth_output_dir = 'depth_maps'
if not os.path.exists(depth_output_dir):
    os.makedirs(depth_output_dir)

for frame in tqdm(frames, "Estimating depth for frames"):
    frame_name = os.path.basename(frame)
    depth_output_path = os.path.join(depth_output_dir, frame_name)
    estimate_depth(frame, depth_output_path)


# Define camera intrinsics
fx, fy = 500, 500  # Focal length
cx, cy = 320, 240  # Principal point (assuming 640x480 resolution)

def depth_to_point_cloud(depth_map, color_image, fx, fy, cx, cy):
    h, w = depth_map.shape
    points = []
    colors = []

    for v in range(h):
        for u in range(w):
            z = depth_map[v, u]
            if z > 0:  # Exclude points with no depth
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points.append([x, y, z])
                colors.append(color_image[v, u] / 255.0)

    points = np.array(points)
    colors = np.array(colors)

    # Create point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd

def combine_point_clouds(depth_maps_dir, images_dir, fx, fy, cx, cy):
    pcd_combined = o3d.geometry.PointCloud()

    depth_images = sorted(os.listdir(depth_maps_dir))
    color_images = sorted(os.listdir(images_dir))
    zipped = list(zip(depth_images, color_images))[::30]
    print(len(zipped))

    for depth_image_name, color_image_name in tqdm(zipped, "collating depth maps"):
        depth_image_path = os.path.join(depth_maps_dir, depth_image_name)
        color_image_path = os.path.join(images_dir, color_image_name)

        depth_map = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED) / 255.0  # Assuming depth maps are normalized
        color_image = cv2.imread(color_image_path)

        pcd = depth_to_point_cloud(depth_map, color_image, fx, fy, cx, cy)
        pcd_combined += pcd

    return pcd_combined

# Define paths
depth_maps_dir = 'depth_maps'

# Combine point clouds from multiple depth maps
combined_pcd = combine_point_clouds(depth_maps_dir, output_dir, fx, fy, cx, cy)

# Visualize the combined point cloud
o3d.visualization.draw_geometries([combined_pcd])