from fastapi import APIRouter, Request, Depends, Response, encoders, File, UploadFile, Form, BackgroundTasks
import typing as t

from torch.multiprocessing import Pool, Process, set_start_method

# from app.core.celery_app import celery_app

# from celery.result import AsyncResult
# from celery.task.control import revoke

import shutil
import os
import json
import sys
import time
import uuid

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

from app.tasks import face_reg_task

# @r.get("/faces/task")
# async def stop_running_task(
#     request: Request,
#     task_id: str
# ):
#     revoke(task_id, terminate=True)

#     return {"result": "ok"}

# from app.tasks import face_reg_task

@r.post("/faces/image")
async def image_face_detection(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str,
    files: t.List[UploadFile] = File(...)
):
    print(request)
    # delete all previous images
    shutil.rmtree(facebank_dir, ignore_errors=False, onerror=None)
    os.makedirs(facebank_dir)

    for file in files:
        with open(os.path.join(facebank_dir, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(face_reg_task, url)
    # face_reg_task(url)
    # created_task = celery_app.send_task("app.tasks.face_reg_task", args=[url])

    return {"result": "ok"}

    # INIT_TIME = time.time()
    
    # net, ln = yolo_detection.init_net()
    # conf = face_verify.init_config()
    # mtcnn = face_verify.init_MTCNN()
    # learner = face_verify.init_learner(conf)
    # targets, names = face_verify.init_facebank(conf=conf, learner=learner, mtcnn=mtcnn)

    # cap = cv2.VideoCapture("./app/droneface/test/input/airport.mp4")

    # # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = 1

    # width = 1280
    # height = 720 # keep original height
    # dim = (width, height)

    # fname = ""
    
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         print("Can't receive frame (stream end?)")
    #         time.sleep(1)
    #     else:
    #         START_TIME = time.time()

    #         # image = cv2.imread("./app/droneface/test/input/DJI_0098_1.jpg")
    #         image = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    #         draw_image = image.copy()

    #         TIME0 = time.time()
            
    #         boxes, confidences, classIDs, detected_image = yolo_detection.detect_bboxes(net, ln, image)

    #         TIME1 = time.time()

    #         faces = []
    #         for i in range(len(boxes)):
    #             # extract the bounding box coordinates
    #             (x, y) = (boxes[i][0], boxes[i][1])
    #             (w, h) = (boxes[i][2], boxes[i][3])

    #             # crop and save face
    #             DELTA_y = int(0.1 * h)
    #             DELTA_x = int(0.2 * w)
    #             #crop_face = image[y:y+h,x:x+w].copy()  
    #             crop_face = image[y-DELTA_y*2:y+h+DELTA_y,x-DELTA_x:x+w+DELTA_x].copy()

    #             #cv2.imwrite("test/output/output_crop/crop_face_{}.png".format(str(i)), crop_face)

    #             pillow_image = Image.fromarray(cv2.cvtColor(crop_face, cv2.COLOR_BGR2RGB))
    #             face = pillow_image.resize((112,112))
    #             faces.append(face)
    #         face_ids = range(len(faces))

    #         TIME2 = time.time()

    #         min_face_id, min_face_score = face_verify.verify_faces(conf=conf, learner=learner, targets=targets, faces=faces, face_ids=face_ids)

    #         TIME3 = time.time()
            
    #         (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
    #         (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])
    #         cv2.rectangle(draw_image, (x, y), (x + w, y + h), (0,255,0), 3)
    #         text = "{}: {:.4f}".format("target face", min_face_score)
    #         cv2.putText(draw_image, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)

    #         shutil.rmtree(static_dir, ignore_errors=False, onerror=None)
    #         os.makedirs(static_dir)
    #         fname = str(time.time()) + ".png"
    #         cv2.imwrite("./app/public/" + fname, draw_image)

    #         TIME4 = time.time()

    # return {
    #     "result": "ok", 
    #     "imageResult": "http://localhost:8000/api/files/" + fname,
    #     # "initTime": START_TIME - INIT_TIME,
    #     # "readImageTime": TIME0 - START_TIME,
    #     # "detectTime": TIME1 - TIME0,
    #     # "processDetectedResultTime": TIME2 - TIME1,
    #     # "verifyTime": TIME3 - TIME2,
    #     # "drawResultTime": TIME4 - TIME3,
    #     # "totalTime": TIME4 - START_TIME
    # }
