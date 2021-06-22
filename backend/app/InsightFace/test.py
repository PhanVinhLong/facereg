from arcface import Recognition
from PIL import Image
import cv2
import time
import shutil
import os
import torch
import random

import yolo_detection

recognition = Recognition()
# recognition.update_facebank()

stream_url="rtsp://rtmp.bahien.com:1935/live/stream"

cap = cv2.VideoCapture(stream_url)
cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))
width = 1280
height = 720
dim = (width, height)

fname = ""

while True:
    print("INFO: start")
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?)")
        print(stream_url)
    else:
        print("INFO: else")
        START_TIME = time.time()

        # image = cv2.imread("./app/droneface/test/input/DJI_0098_1.jpg")
        # image = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        image = frame.copy()
        draw_image = image.copy()

        TIME0 = time.time()
        
        boxes, faces, face_ids = recognition.detect_yolo(image)
        print("INFO: len - ", len(face_ids))
        TIME2 = time.time()
        try:
            min_face_id, min_face_score = recognition.verify_faces(faces=faces, face_ids=face_ids)
            print("MIN FACE ID: ", min_face_id)
        except RuntimeError:
            # oom = True
            continue
        TIME3 = time.time()
        
        (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
        (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])
        #draw_image = image[y:y+h,x:x+w].copy()
        cv2.rectangle(draw_image, (x, y), (x + w, y + h), (0,255,0), 3)
        text = "{}: {:.4f}".format("target face", min_face_score)
        cv2.putText(draw_image, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)

        # shutil.rmtree(static_dir, ignore_errors=False, onerror=None)
        # os.makedirs(static_dir)
        fname = str(time.time()) + ".png"
        print(os.path.realpath(os.path.join("./tests/", fname)))
        draw_image = cv2.resize(draw_image, (384, 216), interpolation = cv2.INTER_AREA)
        cv2.imwrite("./tests/" + fname, draw_image)

        TIME4 = time.time()

        torch.cuda.empty_cache()

        print('time: ', time.time()- START_TIME)
        
        res, im_png = cv2.imencode(".png", draw_image)
        # return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")