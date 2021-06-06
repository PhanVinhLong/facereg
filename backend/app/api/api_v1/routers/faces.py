from fastapi import APIRouter, Request, Depends, Response, encoders, File, UploadFile, Form, BackgroundTasks
import typing as t
import io
from starlette.responses import StreamingResponse

import torch

# from app.core.celery_app import celery_app

# from celery.result import AsyncResult
# from celery.task.control import revoke

import shutil
import os
import json
import sys
import time
import uuid

import random

import cv2
from PIL import Image

sys.path.append("./app/droneface")
sys.path.append("./app/droneface/libs")
sys.path.append("./app/droneface/libs/insight_face/InsightFace_Pytorch")
sys.path.append("./app/droneface/libs/insight_face")

from libs import yolo_detection
from libs.insight_face.InsightFace_Pytorch import face_verify

faces_router = r = APIRouter()

facebank_dir = "./app/droneface/libs/insight_face/InsightFace_Pytorch/data/facebank/current_face"

static_dir = "./app/public"

# from app.tasks import detect_streamface_reg_task

# @app.get("/faces/image/{filename}")
# async def get_file(filename: str):
#     task = celery_app.send_task("app.tasks.get_lasted_image", args=[])
#     result = AsyncResult(id=task.task_id, app=celery_app).get()
#     return result

# from app.tasks import video_feed
# @r.get("/faces/videofeed")
# async def feed_video(
#     request: Request
# ):
#     return video_feed()

net, ln = yolo_detection.init_net()
conf = face_verify.init_config()
mtcnn = face_verify.init_MTCNN()
learner = face_verify.init_learner(conf)
targets, names = face_verify.init_facebank(conf=conf, learner=learner, mtcnn=mtcnn)
stream_url = "./app/droneface/test/input/airport.mp4"
print('-------------- Importedd ----------------')

def init_model():
    print('Init models')

@r.get("/faces/image")
async def get_lasted_result_image(
    request: Request
):
    if not os.path.isdir(static_dir):
        return {"result": "empty"}

    _, _, filenames = next(os.walk(static_dir))
    
    if len(filenames) == 0:
        return {"result": "empty"}

    return {"result": "http://115.78.96.177/api/files/" + filenames[0]}


@r.get("/faces/rimage/{tmp}")
def get_result_image(
    request: Request,
):
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))

    width = 1280
    height = 720
    dim = (width, height)

    fname = ""
    
    if True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?)")
            print(stream_url)
            return Response(status_code=501)
        else:
            START_TIME = time.time()

            # image = cv2.imread("./app/droneface/test/input/DJI_0098_1.jpg")
            # image = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
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
            # cv2.imwrite("./app/public/" + fname, draw_image)

            TIME4 = time.time()

            torch.cuda.empty_cache()

            print('time: ', time.time()- START_TIME)
            
            res, im_png = cv2.imencode(".png", draw_image)
            return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")

    return Response(status_code=501)

    draw_image = cv2.imread('./app/droneface/test/input/DJI_0039_Moment_2_crop.jpg')
    
    res, im_png = cv2.imencode(".png", draw_image)

    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")

@r.post("faces/video")
async def video_face_detection(
    request: Request,
    url: str,
    files: t.List[UploadFile] = File(...)
):
    cap = cv2.VideoCapture(stream_url)
    
    if cap.isOpened():
        ret, frame = cap.read()

from app.tasks import face_reg_task

@r.post("/faces/upload")
async def image_face_detection(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str,
    files: t.List[UploadFile] = File(...)
):
    global stream_url
    stream_url = url

    # delete all previous images
    shutil.rmtree(facebank_dir, ignore_errors=False, onerror=None)
    os.makedirs(facebank_dir)

    for file in files:
        with open(os.path.join(facebank_dir, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # background_tasks.add_task(face_reg_task, url)
    # face_reg_task(url)
    # created_task = celery_app.send_task("app.tasks.face_reg_task", args=[url])

    return {"result": "okk"}
