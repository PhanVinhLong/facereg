# import the necessary libs
import numpy as np
import argparse
import time
import cv2
import os
import sys
from PIL import Image

cwd = os.getcwd()
print("cwd", cwd)

sys.path.append(cwd + "/" + "libs")
sys.path.append(cwd + "/" + "libs/insight_face/InsightFace_Pytorch")
sys.path.append(cwd + "/" + "libs/insight_face")
print("path sys: ")
for line in sys.path:
    print(line)

from libs import yolo_detection
from libs.insight_face.InsightFace_Pytorch import face_verify

#yolo_detection.test_import()

net, ln = yolo_detection.init_net()
print("TEST - yolo detection NET initted")

conf = face_verify.init_config()
mtcnn = face_verify.init_MTCNN()
learner = face_verify.init_learner(conf)
targets, names = face_verify.init_facebank(conf=conf, learner=learner, mtcnn=mtcnn)

def test_face_detection():
    image = cv2.imread("test/input/anhhiep_testmulti.jpg")
    boxes, confidences, classIDs, detected_image = yolo_detection.detect_bboxes(net, ln, image)
    cv2.imwrite("test/output/face_detection.png", detected_image)

    for i in range(len(boxes)):
        # extract the bounding box coordinates
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        crop_face = image[y:y+h,x:x+w].copy()
        cv2.imwrite("test/output/output_crop/crop_face_{}.png".format(str(i)), crop_face)

def test_face_recognition_test_loaded_images():
    print("START TEST FACE RECOG")
    face_verify.verify_images_test(conf=conf, learner=learner, targets=targets)

# on single input image
def test_face_detection_recognition():
    print("START TEST FACE DETECTION RECOG")
    
    #image = cv2.imread("test/input/anhhiep_testmulti.jpg")
    #image = cv2.imread("test/input/DJI_0039_Moment_2_crop.jpg")
    #image = cv2.imread("test/input/DJI_0039_Moment_2.jpg")
    #image = cv2.imread("test/input/DJI_0098_Moment_Moment.jpg")
    image = cv2.imread("test/input/DJI_0098_1.jpg")
    draw_image = image.copy()

    boxes, confidences, classIDs, detected_image = yolo_detection.detect_bboxes(net, ln, image)
    cv2.imwrite("test/output/face_detection.png", detected_image)
    
    START_TIME = time.time()
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

        pillow_image = Image.fromarray(cv2.cvtColor(crop_face, cv2.COLOR_BGR2RGB))
        face = pillow_image.resize((112,112))
        faces.append(face)
    face_ids = range(len(faces))
    min_face_id, min_face_score = face_verify.verify_faces(conf=conf, learner=learner, targets=targets, faces=faces, face_ids=face_ids)
    
    (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
    (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])
    cv2.rectangle(draw_image, (x, y), (x + w, y + h), (0,255,0), 3)
    text = "{}: {:.4f}".format("target face", min_face_score)
    cv2.putText(draw_image, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)


    END_TIME = time.time()
    print("time cost: ", END_TIME - START_TIME)
    
    #'''
    cv2.imwrite("test/output/final_detected_face.png", draw_image)
    #cv2.imshow('detected face on image', cv2.resize(draw_image, (draw_image.shape[1]//3, draw_image.shape[0]//3)))
    #cv2.waitKey()
    #cv2.destroyAllWindows()    
    #'''

# on single video
def test_face_detection_recognition_video():

    BEGIN = 0
    DURATION = 0
    print("START TEST FACE DETECTION RECOG ON SINGLE VIDEO")
    START_TIME = time.time()
    # DJI_0101.MP4, DJI_0098.MP4
    cap = cv2.VideoCapture("test/input/DJI_0101.MP4")
    
    cap.set(cv2.CAP_PROP_POS_MSEC, BEGIN * 1000)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("fps: ", fps)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    # DJI_0101.MP4, DJI_0098.MP4, DJI_0106.MP4
    video_writer = cv2.VideoWriter("test/output/DJI_0101_out.avi",
                                   cv2.VideoWriter_fourcc(*'XVID'), int(fps), (frame_width,frame_height))
    
    if DURATION != 0:
        i = 0
    frame_count = 0
    while cap.isOpened():
        isSuccess,frame = cap.read()
        if isSuccess:            
#             image = Image.fromarray(frame[...,::-1]) #bgr to rgb
            #image = Image.fromarray(frame)
            image = frame.copy()
            print("frame count: ", frame_count)
            #cv2.imwrite("test/output/tmp/tmp_frame_{}.png".format(frame_count), frame)
            if frame_count % 10 != 0:
                video_writer.write(frame)
                frame_count += 1
                continue
            START_TIME_each_frame = time.time()
            try:
                boxes, confidences, classIDs = yolo_detection.detect_bboxes(net, ln, image)
            except:
                boxes = []
                confidences = []
                classIDs = []
                detected_image = 0
            if len(boxes) == 0:
                print('no face')
                print("1 FRAME take time: ", time.time() - START_TIME_each_frame)
                continue
            else:
                #frame_count += 1
                #continue
                faces = []
                for i in range(len(boxes)):
                    # extract the bounding box coordinates
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])

                    # crop and save face
                    DELTA_y = int(0.1 * h)
                    DELTA_x = int(0.2 * w)
                    #crop_face = image[y:y+h,x:x+w].copy()  
                    crop_face_left = max(0, x-DELTA_x)
                    crop_face_right = min(frame_width, x+w+DELTA_x)
                    crop_face_top = max(0, y-DELTA_y*2)
                    crop_face_bottom = min(frame_height, y+h+DELTA_y)
                    crop_face = image[crop_face_top:crop_face_bottom,crop_face_left:crop_face_right].copy()

                    #cv2.imwrite("test/output/output_crop/crop_face_{}.png".format(str(i)), crop_face)

                    pillow_image = Image.fromarray(cv2.cvtColor(crop_face, cv2.COLOR_BGR2RGB))
                    face = pillow_image.resize((112,112))
                    faces.append(face)
                face_ids = range(len(faces))
                min_face_id, min_face_score = face_verify.verify_faces(conf=conf, learner=learner, targets=targets, faces=faces, face_ids=face_ids)
                
                (x, y) = (boxes[min_face_id][0], boxes[min_face_id][1])
                (w, h) = (boxes[min_face_id][2], boxes[min_face_id][3])
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 3)
                text = "{}: {:.4f}".format("target face", min_face_score)
                #cv2.putText(frame, text, (x+w+5, y), cv2.FONT_HERSHEY_SIMPLEX,2, (0,0,255), 4)
            #video_writer.write(frame)
            frame_count += 1
            print("1 FRAME take time: ", time.time() - START_TIME_each_frame)
        else:
            break
        if DURATION != 0:
            i += 1
            if i % 25 == 0:
                print('{} second'.format(i // 25))
            if i > 25 * DURATION:
                break        
    END_TIME = time.time()
    print("Process 1 video take: ", END_TIME - START_TIME)
    cap.release()
    video_writer.release()
    


#test_face_detection()
#face_verify.test_import()
#test_face_recognition_test_loaded_images()
#test_face_detection_recognition()
test_face_detection_recognition_video()
