import cv2
from PIL import Image
import argparse
from pathlib import Path
from multiprocessing import Process, Pipe,Value,Array
import torch
from .config import get_config
from mtcnn import MTCNN
from Learner import face_learner
from utils import load_facebank, draw_box_name, prepare_facebank
import time
import os
import numpy as np

from glob import glob

cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))

#CONSTANT
THRESHOLD = 1.54
UPDATE = True
TTA = ""


def test_import():
    print("test import insight face")
    pass

def init_config():
    config = get_config(False)

    return config

def init_MTCNN():
    mtcnn = MTCNN()
    print('mtcnn loaded')

    return mtcnn

def init_learner(conf):
    
    learner = face_learner(conf, True)
    learner.threshold = THRESHOLD

    if conf.device.type == 'cpu':
        learner.load_state(conf, 'cpu_final.pth', True, True)
    else:
        learner.load_state(conf, 'final.pth', True, True)
    
    learner.model.eval()
    print('learner loaded')
    return learner

def init_facebank(conf, learner, mtcnn):
    if UPDATE:
        targets, names = prepare_facebank(conf, learner.model, mtcnn, tta = TTA)
        print('facebank updated')
    else:
        targets, names = load_facebank(conf)
        print('facebank loaded')
    
    return targets, names


def verify_images_test(conf, learner, targets):

    ###### DEBUG
    frame = cv2.imread(dir_path + "/" + "test_face_images/anhhiep_testmulti.jpg")
    # image = Image.fromarray(frame[...,::-1]) #bgr to rgb
    image = Image.fromarray(frame)

    faces_paths = sorted(glob(dir_path + "/" + "test_face_images/test_single_faces/*.jpg"))
    faces_paths = sorted(glob(dir_path + "/" + "test_face_images/output_crop (copy 1)/*.png"))
    faces_paths = sorted(glob(dir_path + "/" + "test_face_images/output_crop_small/*.png"))
    faces = list([])
    print("faces_paths", faces_paths)
    for path in faces_paths:

        #face = Image.open("test_face_images/anhHiep_2.jpg")
        face = Image.open(path)
        face = face.resize((112,112))
        #faces.save("test_face_images/test_faces_crop.png")
        faces.append(face)

    print(type(faces), len(faces))
    print(type(faces[0]))
    print(faces[0].size)
    START_TIME = time.time()
    results, score = learner.infer(conf, faces, targets, TTA)
    #frame = draw_box_name([0,0,0,0], '_{:.2f}'.format(score[0]), frame)
    '''
    for idx,bbox in enumerate(bboxes):
        if args.score:
            print(score[idx])
            frame = draw_box_name(bbox, '_{:.2f}'.format(score[idx]), frame)
        else:
            frame = draw_box_name(bbox, names[results[idx] + 1], frame)
    #'''
    print(*list(zip(faces_paths,results,score)), sep="\n")
    MIN_score = 999
    MIN_face_path = ""
    for face_path, result, score in zip(faces_paths,results,score):
        if score < MIN_score:
            MIN_score = score 
            MIN_face_path = face_path
    END_TIME = time.time()
    print(MIN_face_path, MIN_score, END_TIME - START_TIME)
    cv2.imwrite("test_face_images/verify_result.png", frame)

    
    min_face_image = cv2.imread(MIN_face_path)
    cv2.putText(min_face_image, str(MIN_score),(20,20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0,0,255), 1)
    cv2.imshow('min face verify', min_face_image)
    cv2.waitKey()
    cv2.destroyAllWindows()    


def verify_faces(conf, learner, targets, faces, face_ids):
    """
    main function to verify a list of images

    Input:
        - conf:
        - learner:
        - targets:
        - faces: list of pillow-format images

    """
    #print(type(faces), len(faces))
    #print(type(faces[0]))
    #print(faces[0].size)
    START_TIME = time.time()
    results, score = learner.infer(conf, faces, targets, TTA)
    #frame = draw_box_name([0,0,0,0], '_{:.2f}'.format(score[0]), frame)
    '''
    for idx,bbox in enumerate(bboxes):
        if args.score:
            print(score[idx])
            frame = draw_box_name(bbox, '_{:.2f}'.format(score[idx]), frame)
        else:
            frame = draw_box_name(bbox, names[results[idx] + 1], frame)
    #'''
    #print(*list(zip(face_ids,results,score)), sep="\n")
    MIN_score = 999
    MIN_face_id = ""
    for face_id, result, score in zip(face_ids,results,score):
        if score < MIN_score:
            MIN_score = score 
            MIN_face_id = face_id
    END_TIME = time.time()
    print(MIN_face_id, MIN_score, END_TIME - START_TIME)
    #cv2.imwrite("test_face_images/verify_result.png", frame)

    
    min_face_image = faces[MIN_face_id]
    min_face_image = cv2.cvtColor(np.array(min_face_image), cv2.COLOR_RGB2BGR) 
    #cv2.putText(min_face_image, str(MIN_score),(20,20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0,0,255), 1)
    '''
    cv2.imshow('min face verify', min_face_image)
    cv2.waitKey()
    cv2.destroyAllWindows()    
    #'''

    return MIN_face_id, MIN_score