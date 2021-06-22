import sys
sys.path.append("./app/InsightFace")
from arcface import Recognition
from PIL import Image
import cv2
import time
import shutil
import os
import torch
import random

recognition = Recognition()
# recognition.update_facebank()

stream_url="https://demo.bahien.com/live/stream/playlist.m3u8"

# im_tile_resize = concat_tile_resize([[im1], [im1, im2, im1, im2, im1], [im1, im2, im1]])

cap = cv2.VideoCapture(stream_url)
cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))
width = 1280
height = 720
dim = (width, height)

fname = ""

recognition.update_old_facebank(stream_url)
flag, encodedImage = recognition.cap_and_draw_min_face()
cv2.imwrite("test.png", encodedImage)