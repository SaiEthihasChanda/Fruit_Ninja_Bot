import cv2
from pyautogui import *
import pyautogui
import time
import win32api
import win32con
from PIL import ImageGrab, Image
from collections import Counter
import numpy as np

# Function to click at specified coordinates
def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def calculate_unique_colors(image):
    # Flatten the image into a 1D array of RGB tuples
    pixels = image.reshape(-1, 3)

    # Count the number of unique colors
    unique_colors = len(np.unique(pixels, axis=0))

    return unique_colors

def calculate_dominant_colors(image, num_colors=5):
    # Flatten the image into a 1D array of RGB tuples
    pixels = image.reshape(-1, 3)

    # Count the occurrence of each color
    color_counts = Counter(map(tuple, pixels))

    # Find the top 'num_colors' colors with the maximum count
    dominant_colors = [color for color, _ in color_counts.most_common(num_colors)]

    return dominant_colors

def classify_pixels(image):
    # Convert the image to grayscale
    grayscale_image = np.array(Image.fromarray(image).convert('L'))

    # Threshold the grayscale image to separate background and fruit pixels
    threshold = 100  # Adjust as needed
    background_pixels = grayscale_image < threshold

    # Invert the classification to mark fruit pixels
    fruit_pixels = ~background_pixels

    return fruit_pixels


# Initialize the VideoWriter object
found = False
left = None
top = None
width = None
height = None
region = None
video_width = width
video_height = height
fps = 60  # Adjust as needed
video_writer = None

def video():
    video_writer = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width, video_height))

# Search for the board image and fruit image within the region of the board
while True:
    try:
        # Find the board image
        if not found:
            if not pyautogui.locateOnScreen('start.png', confidence=0.5):
                print("Board not found on the screen")
                continue

            # Board image found, get its location
            board_location = pyautogui.locateOnScreen('start.png', confidence=0.5)
            left, top, width, height = board_location

            # Define the region of interest (board area)
            region = (left, top, width, height)

            found = True
            video()
            print("found")




        else:
            # Search for the fruit image within the cropped region of the board
            screenshot = ImageGrab.grab(
                bbox=(left + width * 0.2, top + height * 0.2, left + int(width * 0.8), top + int(height * 0.8)))

            # Convert the screenshot to a numpy array for efficient processing
            screenshot_np = np.array(screenshot)

            # Classify pixels as background or fruit based on brightness
            background_pixels = classify_pixels(screenshot_np)

            # Create a black canvas of the same size as the original image
            black_canvas = np.zeros_like(screenshot_np)

            # Fill the black canvas with the original image except for the background pixels
            black_canvas[background_pixels] = screenshot_np[background_pixels]

            print("frame")

            # Convert to BGR color space for displaying
            bgr_black_canvas = cv2.cvtColor(black_canvas, cv2.COLOR_RGB2BGR)

            # Display the frame
            cv2.imshow('Frame', bgr_black_canvas)
            cv2.moveWindow('Frame', 1000, 500)

            # Set the initial cursor position to the leftmost side of the region
            cursor_x = left + int(width * 0.2)
            cursor_y = top + int(height * 0.5)  # Center of the region vertically

            # Set initial state for mouse button
            is_mouse_down = False

            # Continuous fast swiping of the mouse pointer from left to right
            cursor_x = left + int(width * 0.2)  # Start from the leftmost side
            cursor_y = top + int(height * 0.5)  # Center of the region vertically

            while cursor_x < left + int(width * 0.8):
                try:
                    # Check if the current pixel is black
                    #if np.all(black_canvas[cursor_y - top, cursor_x - left] != [0, 0, 0]):
                        # Move the cursor to the next position
                    win32api.SetCursorPos((cursor_x, cursor_y))

                        # Perform mouse click action
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, cursor_x, cursor_y, 0, 0)
                    #else:
                        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, cursor_x, cursor_y, 0, 0)
                except IndexError:
                    pass
                cursor_x += 50  # Adjust the speed of swiping as needed
                time.sleep(0.01)

                    # Check for key press to stop the script
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


            # Write the frame to the video

    except ImageNotFoundException as e:
        print("Image not found:", e)

# Release the VideoWriter object
video_writer.release()
print("Video generated.")
