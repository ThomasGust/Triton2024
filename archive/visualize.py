import open3d as o3d
import numpy as np

def visualize_point_cloud(point_cloud):
    # Convert the point cloud to an Open3D format
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    
    # Visualize the point cloud
    o3d.visualization.draw_geometries([pcd])

if __name__ == "__main__":
    # Load the point cloud from the saved file
    point_cloud = np.load("point_cloud.npy")
    
    # Visualize the point cloud
    visualize_point_cloud(point_cloud)