import cv2
import numpy as np

def main():
    # Load the image
    image = cv2.imread('video\\frames\\520.png')
    image = cv2.resize(image, [int(image.shape[1]/2), int(image.shape[0]/2)])
    if image is None:
        print("Error: Image could not be read.")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform Canny edge detection
    edged = cv2.Canny(blurred, 150, 175)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the contours
    for contour in contours:
        # Approximate the contour to reduce the number of points
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # Draw the contour and its vertices
        cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)  # Draw contour in green

        # Draw each point on the contour
        for (x, y) in approx.reshape(-1, 2):
            cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # Draw vertex in red

    # Display the image with contours and vertices
    cv2.imshow('Contours and Vertices', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
