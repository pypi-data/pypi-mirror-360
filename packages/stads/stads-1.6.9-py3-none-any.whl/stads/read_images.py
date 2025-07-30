import cv2
import numpy as np


def get_frames_from_mp4(videoPath, NumberOfFrames):
    cap = cv2.VideoCapture(videoPath)
    frameNumber = 0
    frames = []

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or (NumberOfFrames and frameNumber >= NumberOfFrames):
            break
        greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(greyFrame)
        frameNumber = frameNumber + 1

    cap.release()
    return np.array(frames)
