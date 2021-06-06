from app.core.celery_app import celery_app
import cv2
import os
import matplotlib.pyplot as plt
from app.db.schemas import DetectionEdit
import numpy
import subprocess
import moviepy.editor as moviepy

from torch.multiprocessing import Pool, Process, set_start_method

from PIL import Image
import time

from fastapi.responses import FileResponse, StreamingResponse

static_dir = "./app/public"

# from app.db.session import SessionLocal, Base, engine

# import sys
# sys.path.append(os.path.realpath('./app/yolov4'))

# from tool.utils import *
# from tool.torch_utils import *
# from tool.darknet2pytorch import Darknet

from app.db.session import get_db

from app.yolov4.tool.utils import *
from app.yolov4.tool.torch_utils import *
from app.yolov4.tool.darknet2pytorch import Darknet

from app.db.crud import edit_detection

from app.core import config

import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core import config

import colorsys
import math
import random

import shutil
import os
import json
import sys
import time
import uuid

sys.path.append("./app/droneface")
sys.path.append("./app/droneface/libs")
sys.path.append("./app/droneface/libs/insight_face/InsightFace_Pytorch")
sys.path.append("./app/droneface/libs/insight_face")

from libs import yolo_detection
from libs.insight_face.InsightFace_Pytorch import face_verify

facebank_dir = "./app/droneface/libs/insight_face/InsightFace_Pytorch/data/facebank/current_face"

static_dir = "./app/public"

net, ln = yolo_detection.init_net()
conf = face_verify.init_config()
mtcnn = face_verify.init_MTCNN()
learner = face_verify.init_learner(conf)
targets, names = face_verify.init_facebank(conf=conf, learner=learner, mtcnn=mtcnn)
stream_url = "./app/droneface/test/input/DJI_0101.MP4"
cap = cv2.VideoCapture(stream_url)

def gen_frames():  
    while True:
        success, frame = cap.read()  # read the frame
        if not success:
            print("no frame")
            time.sleep(0.3)
            continue
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            time.sleep(0.3)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@celery_app.task(acks_late=True)
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace;boundary=frame")

@celery_app.task(acks_late=True)
def face_reg_task(url: str) -> str:

    INIT_TIME = time.time()
    
    # net, ln = yolo_detection.init_net()
    # conf = face_verify.init_config()
    # mtcnn = face_verify.init_MTCNN()
    # learner = face_verify.init_learner(conf)
    # targets, names = face_verify.init_facebank(conf=conf, learner=learner, mtcnn=mtcnn)

    cap = cv2.VideoCapture(url)
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 1

    width = 1280
    height = 720 # keep original height
    dim = (width, height)

    fname = ""

    counter = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            counter = counter + 1
            if counter >= 10:
                break
            print("Can't receive frame (stream end?)")
            time.sleep(1)
        else:
            counter = 0

            START_TIME = time.time()

            # image = cv2.imread("./app/droneface/test/input/DJI_0098_1.jpg")
            #image = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            image = frame.copy()
            draw_image = image.copy()

            TIME0 = time.time()
            
            boxes, confidences, classIDs = yolo_detection.detect_bboxes(net, ln, image)

            TIME1 = time.time()

            boxes = boxes[:20]
            faces = []
            for i in range(len(boxes)):
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                # crop and save face
                DELTA_y = int(0.1 * h)
                DELTA_x = int(0.2 * w)
                
                #crop_face = image[y:y+h,x:x+w].copy()  
                crop_face = image[y-DELTA_y*2:y+h+DELTA_y,x-DELTA_x:x+w+DELTA_x].copy()

                #cv2.imwrite("test/output/output_crop/crop_face_{}.png".format(str(i)), crop_face)
                try:
                    pillow_image = Image.fromarray(cv2.cvtColor(crop_face, cv2.COLOR_BGR2RGB))
                    face = pillow_image.resize((112,112))
                    faces.append(face)
                except:
                    continue
            face_ids = range(len(faces))

            TIME2 = time.time()

            min_face_id, min_face_score = face_verify.verify_faces(conf=conf, learner=learner, targets=targets, faces=faces, face_ids=face_ids)

            TIME3 = time.time()
            
            (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
            (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])
            #draw_image = image[y:y+h,x:x+w].copy()
            cv2.rectangle(draw_image, (x, y), (x + w, y + h), (0,255,0), 3)
            text = "{}: {:.4f}".format("target face", min_face_score)
            cv2.putText(draw_image, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)

            shutil.rmtree(static_dir, ignore_errors=False, onerror=None)
            os.makedirs(static_dir)
            fname = str(time.time()) + ".png"
            # print(os.path.realpath(os.path.join("./app/public/", fname)))
            draw_image = cv2.resize(draw_image, (384, 216), interpolation = cv2.INTER_AREA)
            cv2.imwrite("./app/public/" + fname, draw_image)

            TIME4 = time.time()

            torch.cuda.empty_cache()

            # time.sleep(2.5)

            print('time: ', time.time()- START_TIME)

    return "ok"