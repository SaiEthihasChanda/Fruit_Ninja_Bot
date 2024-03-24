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
# Search for the board image and fruit image within the region of the board
while True:
    try:
        # Find the board image
        if found == False:
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


            screenshot = ImageGrab.grab(
                bbox=(left + width * 0.1, top + height * 0.2, left + int(width * 0.9), top + int(height * 0.9)))
            screenshot_np = np.array(screenshot)

            background_pixels = classify_pixels(screenshot_np)


            black_canvas = np.zeros_like(screenshot_np)

            black_canvas[background_pixels] = screenshot_np[background_pixels]
            print("frame")
            bgr_black_canvas = cv2.cvtColor(black_canvas, cv2.COLOR_RGB2BGR)

            cv2.imshow('Frame', bgr_black_canvas)
            cv2.moveWindow('Frame', 1000, 500)
            cv2.waitKey(1)

            # Write the frame to the video


    except ImageNotFoundException as e:
        print("Image not found:", e)

    except KeyboardInterrupt:
        # If the script is stopped, release the VideoWriter object
        print("Script stopped. Generating video...")
        break

# Release the VideoWriter object
video_writer.release()
print("Video generated.")
