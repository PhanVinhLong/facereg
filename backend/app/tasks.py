from app.core.celery_app import celery_app
import cv2
import os
import matplotlib.pyplot as plt
from app.db.schemas import DetectionEdit
import numpy
import subprocess
import moviepy.editor as moviepy

from PIL import Image
import time

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

# Dependency
def get_db():
    db = SessionLocal()

use_cuda = True
class_names = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'tricycle', 'awning-tricycle', 'bus', 'motor']

def create_model(model_id):
    model_names = ['yolo-init', 'yolo-r', 'yolo-a', 'yolo-n', 'yolo-final']
    model_name = model_names[model_id - 1]
    config_file = os.path.join('./app/detection/models', model_name, 'config.cfg')
    weight_file = os.path.join('./app/detection/models', model_name, 'model.weights')
    model = Darknet(config_file)
    model.load_weights(weight_file)
    model.cuda()
    return model

def draw_bbox(img, bboxes, classes):
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    show_label = True
    image_h, image_w, _ = img.shape
    num_classes = len(classes)
    hsv_tuples = [(1.0 * x / num_classes + 10, 1., 1.)
                  for x in range(num_classes + 10)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    # out_boxes, out_scores, out_classes, num_boxes = bboxes
    for i in range(len(bboxes)):
        x1 = int(bboxes[i][0])
        y1 = int(bboxes[i][1])
        x2 = int(bboxes[i][2])
        y2 = int(bboxes[i][3])
        conf = float(bboxes[i][5])
        class_id = int(bboxes[i][6])
        if class_id < 0 or class_id > num_classes:
            continue

        fontScale = 0.5
        score = conf
        class_ind = class_id
        bbox_color = colors[class_id]
        bbox_thick = int(0.6 * (image_h + image_w) / 600)
        c1, c2 = (x1, y1), (x2, y2)
        cv2.rectangle(img, c1, c2, bbox_color, bbox_thick)

        if show_label:
            bbox_mess = '%s: %.2f' % (classes[class_ind], score)
            t_size = cv2.getTextSize(
                bbox_mess, 0, fontScale, thickness=bbox_thick // 2)[0]
            c3 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
            cv2.rectangle(img, c1, (np.float32(c3[0]), np.float32(
                c3[1])), bbox_color, -1)  # filled

            cv2.putText(img, bbox_mess, (c1[0], np.float32(c1[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale, (0, 0, 0), bbox_thick // 2, lineType=cv2.LINE_AA)
    return img

def detect_yolo(model, img):

    class_names = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'tricycle', 'awning-tricycle', 'bus', 'motor']

    height, width, _ = img.shape
    sized = cv2.resize(img, (model.width, model.height))
    sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)
    
    result = []

    for i in range(2):
        boxes = do_detect(model, sized, 0.4, 0.6, use_cuda)[0]

        if i==1:
            for box in boxes:
                box[0] = int(box[0] * width)
                box[1] = int(box[1] * height)
                box[2] = int(box[2] * width)
                box[3] = int(box[3] * height)
                result.append(box)
    return result

def detect_image(model_id, detection_id, ori_image_path, res_image_path):
    model = create_model(model_id)
    
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    db = SessionLocal()
    updated_detection = edit_detection(db, detection_id, DetectionEdit(status='Detecting'))
    
    ext = ori_image_path.split('.')[-1]
    img = numpy.array([])
    if ext == 'png':
        img = cv2.imread(ori_image_path)
    else:
        img = numpy.array(Image.open(ori_image_path).convert('RGB'))[:, :, ::-1].copy()
    result = detect_yolo(model, img)
    res_img = draw_bbox(img, result, class_names)
    cv2.imwrite(res_image_path, res_img)
    d_result = []
    for box in result:
        d_result.append({
            'class': class_names[int(box[6])],
            'x1': box[0],
            'y1': box[1],
            'x2': box[2],
            'y2': box[3],
            'conf': str(box[5])
        })

    updated_detection = edit_detection(db, detection_id, DetectionEdit(status='Done', results=json.dumps(d_result)))

def detect_video(model_id, detection_id, ori_image_path, res_image_path):
    model = create_model(model_id)

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    db = SessionLocal()
    updated_detection = edit_detection(db, detection_id, DetectionEdit(status='Detecting'))

    cap = cv2.VideoCapture(ori_image_path)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    avi_res_image_path = res_image_path + '.avi'
    out = cv2.VideoWriter(avi_res_image_path ,fourcc, fps, (int(width),int(height)))

    d_results = []
    flgg = True
    for i in range(num_frames):
        start_time = time.time()
        success, img = cap.read()
        result = detect_yolo(model, img)
        res_img = draw_bbox(img, result, class_names)
        out.write(res_img)
        print(i, ':', 'time', time.time() - start_time)
    print('done - total: ', num_frames)
    
    cap.release()
    out.release()

    clip = moviepy.VideoFileClip(avi_res_image_path, verbose=False)
    clip.write_videofile(res_image_path, verbose=False)
    os.remove(avi_res_image_path)

    updated_detection = edit_detection(db, detection_id, DetectionEdit(status='Done'))


def detect_stream(model_id, detection_id, ori_url, res_url):

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    db = SessionLocal()
    updated_detection = edit_detection(db, detection_id, DetectionEdit(status='Detecting'))

    model = create_model(model_id)
    cap = cv2.VideoCapture(ori_url)

    # fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 10
    width = width if width > 0 else 640
    height = height if height > 0 else 320 

    print('streamiing to:', res_url)

    # command and params for ffmpeg
    command = ['ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-f', 'flv',
            res_url]
    p = subprocess.Popen(command, stdin=subprocess.PIPE)

    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    # out = cv2.VideoWriter('./app/public/' + str(detection_id) + '.avi' ,fourcc, fps, (int(width),int(height)))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?)")
            time.sleep(1)
        else:
            start_time = time.time()
            result = detect_yolo(model, frame)
            res_img = draw_bbox(frame, result, class_names)
            p.stdin.write(res_img.tobytes())
            # out.write(res_img)
            time.sleep(0.25)
            # console.log('timing: ', time.time() - start_time)

    cap.release()
    # out.release()

@celery_app.task(acks_late=True)
def stream_detection_task(model_id: int, detection_id: int, ori_url: str, res_url: str) -> str:
    
    detect_stream(model_id, detection_id, ori_url, res_url)

    return "Detection request received"

@celery_app.task(acks_late=True)
def example_task(word: str) -> str:
    return f"test task returns {word}"

@celery_app.task(acks_late=True)
def detection_task(model_id: int, detection_id: int, ori_filename: str, res_filename: str, detection_type: str) -> str:
    ori_image_path = os.path.join('./app/public', ori_filename)
    res_image_path = os.path.join('./app/public', res_filename)

    if detection_type=='Image':
        result = detect_image(model_id, detection_id, ori_image_path, res_image_path)
    else:
        result = detect_video(model_id, detection_id, ori_image_path, res_image_path)

    return "Detection request received"