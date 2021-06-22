import cv2
from PIL import Image
from multiprocessing import Process, Pipe, Value, Array
import torch
from config import get_config
from mtcnn import MTCNN
from Learner  import face_learner
from utils import load_facebank, draw_box_name, prepare_facebank
import time
import shutil
import yolo_detection
import os
import random

from yolov4.tool.utils import *
from yolov4.tool.torch_utils import *
from yolov4.tool.darknet2pytorch import Darknet

THRESHOLD = 1.54
FACEBANK_DIR = "./app/InsightFace/data/facebank/current_face"
config_file = "./app/InsightFace/yolov4/models/yolov4-tiny-3l.cfg"
weight_file = "./app/InsightFace/yolov4/models/yolov4-tiny-3l.weights"

class Recognition:
    def __init__(self):
        self.stream_url = "https://demo.bahien.com/live/stream/playlist.m3u8"
        self.cap = cv2.VideoCapture(self.stream_url)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.conf = get_config(False)
        self.mtcnn = MTCNN()
        self.learner = face_learner(self.conf, True)
        self.learner.threshold = THRESHOLD
        self.learner.load_state(self.conf, 'final.pth', True, True)
        self.learner.model.eval()
        print('learner loaded')
        self.targets, self.names = load_facebank(self.conf)
        print('facebank loaded')
        self.net, self.ln = yolo_detection.init_net()
        print('yolo model loaded')
        # self.model = Darknet(config_file)
        # self.model.load_weights(weight_file)
        # self.model.cuda()

    def update_facebank(self, files, stream_url):
        self.stream_url = stream_url
        self.cap = cv2.VideoCapture(self.stream_url)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        shutil.rmtree(FACEBANK_DIR, ignore_errors=False, onerror=None)
        os.makedirs(FACEBANK_DIR)
        for file in files:
            with open(os.path.join(FACEBANK_DIR, file.filename), "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        self.targets, self.names = prepare_facebank(self.conf, self.learner.model, self.mtcnn, tta = True)
        print('facebank updated')

    def verify_faces(self, faces, face_ids):
        START_TIME = time.time()
        with torch.no_grad():
            results, score = self.learner.infer(self.conf, faces, self.targets, True)
        MIN_score = 999
        MIN_face_id = ""
        for face_id, result, score in zip(face_ids,results,score):
            if score < MIN_score:
                MIN_score = score 
                MIN_face_id = face_id
        END_TIME = time.time()
        return MIN_face_id, MIN_score

    def detect_yolo(self, image):
        boxes, confidences, classIDs = yolo_detection.detect_bboxes(self.net, self.ln, image)
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
        return boxes, faces, face_ids

    # def detect_yolo_gpu(img):
        height, width, _ = img.shape
        sized = cv2.resize(img, (self.model.width, self.model.height))
        sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

        result = []
        faces = []
        for i in range(2):
            boxes = do_detect(model, sized, 0.4, 0.6, use_cuda)[0]
            if i==1:
                for box in boxes:
                    x = int(box[0] * width)
                    y = int(box[1] * height)
                    w = int(box[2] * width) - x
                    h = int(box[3] * height) - y
                    result.append([x, y, w, h])

                    # crop and save face
                    DELTA_y = int(0.1 * h)
                    DELTA_x = int(0.2 * w)
                    crop_face = img[y-DELTA_y*2:y+h+DELTA_y,x-DELTA_x:x+w+DELTA_x].copy()

                    try:
                        pillow_image = Image.fromarray(cv2.cvtColor(crop_face, cv2.COLOR_BGR2RGB))
                        face = pillow_image.resize((112,112))
                        faces.append(face)
                    except:
                        continue
        face_ids = range(len(faces))
        return result, faces, face_ids

    def draw_min_face(self, image):
        TIME1 = time.time()
        boxes, faces, face_ids = self.detect_yolo(image)
        if(len(face_ids) == 0):
            return image
        TIME2 = time.time()
        try:
            min_face_id, min_face_score = self.verify_faces(faces=faces, face_ids=face_ids)
        except RuntimeError:
            return image
        TIME3 = time.time()
        (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
        (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])

        cv2.rectangle(image, (x, y), (x + w, y + h), (0,255,0), 3)
        text = "{}: {:.4f}".format("target", min_face_score)
        cv2.putText(image, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)

        image = cv2.resize(image, (768, 432), interpolation = cv2.INTER_AREA)
        torch.cuda.empty_cache()
        res, im_png = cv2.imencode(".png", image)
        TIME4 = time.time()

        print(f"Detect: {TIME2-TIME1}, Insight: {TIME3-TIME2}, Post proc: {TIME4-TIME3}, Total: {TIME4-TIME1}")

        # fname = str(time.time()) + ".png"
        # cv2.imwrite("./app/droneface/libs/insight_face/InsightFace_Pytorch/tests/" + fname, image)
        # print("./app/droneface/libs/insight_face/InsightFace_Pytorch/tests/" + fname)
        return im_png

    def cap_and_draw_min_face(self):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, random.randint(3, 1000))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        ret, frame = self.cap.read()
        print(self.stream_url)
        if not ret:
            print("ERROR: cannot cap the frame")
            return False, frame
        return True, self.draw_min_face(frame)
        