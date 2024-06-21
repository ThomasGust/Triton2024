import cv2
import numpy as np

def detect_red_square(image):
    # Convert to HSV color space for easier color detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define the range for red color
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    # Combine the masks for red in different HSV ranges
    mask = mask1 + mask2

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # adjust size threshold as needed
            # Approximate the contour to a polygon
            epsilon = 0.05 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 4:  # Check if the approximated contour has 4 sides
                return approx.reshape((4, 2))
    return None

def draw_detected_square(image, points):
    if points is not None:
        # Draw the outline of the square
        cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=3)
        # Draw the corners of the square
        for x, y in points:
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
    return image
def unskew_entire_image(image, src_points):
    """
    Unskew an entire image using the coordinates of a distorted square, aligning the square to be orthogonal.

    :param image: Input image with a distorted square
    :param src_points: Coordinates of the square in the image [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :return: Unskewed entire image
    """
    # Convert src_points to a float32 numpy array
    src_points = np.array(src_points, dtype=np.float32)

    # Determine the width and height of the image
    height, width = image.shape[:2]

    # Use the width and height to decide on the scaling of the destination points
    width_dst = max(np.linalg.norm(src_points[0] - src_points[1]), np.linalg.norm(src_points[2] - src_points[3]))
    height_dst = max(np.linalg.norm(src_points[1] - src_points[2]), np.linalg.norm(src_points[3] - src_points[0]))

    # Adjust the dst_points based on the image dimensions
    dst_points = np.array([
        [src_points[0][0], src_points[0][1]],
        [src_points[0][0] + width_dst, src_points[0][1]],
        [src_points[0][0] + width_dst, src_points[0][1] + height_dst],
        [src_points[0][0], src_points[0][1] + height_dst]
    ], dtype=np.float32)

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Perform the warp perspective
    unskewed_image = cv2.warpPerspective(image, matrix, (width, height))

    return unskewed_image

def detect_pvc_pipes(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found")
        return

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection using Canny
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    
    # Check if lines were found
    if lines is not None:
        # Draw lines on the image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)

    # Show the result
    cv2.imshow('Detected Pipes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

for i in range(100):
    image = detect_pvc_pipes(f'video\\frames\\{i*10}.png')
    """
    image = cv2.resize(image, (int(image.shape[0]/2), int(image.shape[1]/2)))
    red_square = detect_red_square(image)


    if red_square is not None:
        # Draw the detected red square and its corners for debugging
        debug_image = draw_detected_square(image.copy(), red_square)
        cv2.imwrite("red.png", debug_image)
        cv2.imshow('Detected Red Square', debug_image)
        cv2.waitKey(0)

        # Warp the perspective
        warped_image = unskew_entire_image(image, red_square)
        cv2.imshow('Warped Image', warped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Red square not detected.")
    """