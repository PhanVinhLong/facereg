# import the necessary libs
import numpy as np
import argparse
import time
import cv2
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
#print("dit_path", dir_path)
OUTPUT_TEST_FOLDER = dir_path + "/" + "../test"

#some constant
CONFIDENCE = 0.45
NMS_THRESHOLD = 0.3

# load the class labels our YOLO model was trained on
labelsPath = dir_path + "/" + "../config_files/yolo_config/obj.names"
LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colors to represent each possible class label (red and green)
COLORS = [[0,0,255]]

# derive the paths to the YOLO weights and model configuration
weightsPath = dir_path + "/" + "../config_files/yolo_config/yolov4-tiny-3l.weights"
configPath = dir_path + "/" + "../config_files/yolo_config/yolov4-tiny-3l.cfg"

def init_net():
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()

    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return net, ln

def detect_bboxes(net, ln, image):
    """
    yolo detect face bboxes

    Input:
        - net: yolo net
        - ln: yolo layer name
        - image: opencv format image
    
    Output:
        - nms_bboxes: list bbox of detected face
        - nms_confidences: confidences score 
        - nms_classIDs: class id of each bbox (almost 0 - face)
        - image: image with drawed bboxes
    """
    (H, W) = image.shape[:2]
    #draw_image = image.copy()

    #blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),swapRB=True, crop=False)
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (608, 608),swapRB=True, crop=False)
    #blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (832, 832),swapRB=True, crop=False)
    #blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (1024, 1024),swapRB=True, crop=False)
    #blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (1440, 1440),swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln) #list of 3 arrays, for each output layer.

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []
    nms_boxes = []
    nms_confidences = []
    nms_classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:

        # loop over each of the detections
        for detection in output:

            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:] #last 2 values in vector
            classID = np.argmax(scores)
            confidence = scores[classID]
            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > CONFIDENCE:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply NMS to suppress weak, overlapping bounding
    # boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE, NMS_THRESHOLD)
    
    filtered_classids=np.take(classIDs,idxs)

    # ensure at least one detection exists
    if len(idxs) > 0:

        # loop over the indexes we are keeping
        for i in idxs.flatten():
            
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            # draw a bounding box rectangle and label on the image
            color = [int(c) for c in COLORS[classIDs[i]]]
            
            ### update final result after NMS
            nms_boxes.append(boxes[i])
            nms_confidences.append(confidences[i])
            nms_classIDs.append(classIDs[i])


            ### DEBUG save cropped face
            # crop and save face
            DELTA_y = int(0.1 * h)
            DELTA_x = int(0.2 * w)
            #crop_face = image[y:y+h,x:x+w].copy()
            #crop_face = origin_image[y-DELTA_y*2:y+h+DELTA_y,x-DELTA_x:x+w+DELTA_x].copy()
            #print(i, crop_face.shape)
            #cv2.imwrite(OUTPUT_TEST_FOLDER + "/" + "output/output_crop/crop_face_{}.png".format(str(i)), crop_face)
            ### END DEBUG
            
            #cv2.rectangle(draw_image, (x, y), (x + w, y + h), color, 1)
            text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
            #cv2.putText(draw_image, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX,0.5, color, 1)
    
    
    return nms_boxes, nms_confidences, nms_classIDs

def test_import():
    print("test import yolo_detection")
    print(labelsPath)
    print(LABELS)
    pass
