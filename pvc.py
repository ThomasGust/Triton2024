import cv2
import numpy as np

def detect_pvc_structures(image_path):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print("Image not found")
        return

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define color ranges for thresholding
    # Adjust these values based on your specific lighting and color conditions
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])

    # Thresholding for white (PVC pipes)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    # Thresholding for black (joints)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)

    # Find contours for white mask
    contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Find contours for black mask
    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on the original image
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours_white, -1, (0, 255, 0), 3)  # Draw white contours in green
    cv2.drawContours(img_contours, contours_black, -1, (255, 0, 0), 3)  # Draw black contours in blue

    # Display the results
    cv2.imshow('Original Image', img)
    cv2.imshow('White Mask', mask_white)
    cv2.imshow('Black Mask', mask_black)
    cv2.imshow('Detected Pipes and Joints', img_contours)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Use the function with an image file path
detect_pvc_structures('video\\frames\\630.png')
