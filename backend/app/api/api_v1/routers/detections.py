from fastapi import APIRouter, Request, Depends, Response, encoders, File, UploadFile, Form
import typing as t

from app.db.session import get_db
from app.db.crud import (
    get_detections,
    create_detection,
    create_stream_detection,
    get_detection,
    edit_detection
)
from app.db.schemas import DetectionCreate, Detection, DetectionEdit
from app.core.auth import get_current_active_user, get_current_active_superuser

from app.core.celery_app import celery_app

import shutil
import os
import json

detections_router = r = APIRouter()

static_dir = "./app/public"

# @r.post("/detections", response_model=Detection, response_model_exclude_none=True)
# async def detection_create(
#     request: Request,
#     detection: DetectionCreate,
#     db=Depends(get_db),
#     # current_user=Depends(get_current_active_superuser),
# ):
#     """
#     Create a new detection
#     """
#     return create_detection(db, detection)

from app.tasks import detect_stream
@r.post("/detections/stream")
async def stream_detection_create(
    request: Request,
    detection: DetectionCreate = Depends(DetectionCreate.as_form),
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):

    detection = create_stream_detection(db, detection)

    created_task = celery_app.send_task("app.tasks.stream_detection_task", args=[detection.model_id, detection.id, detection.ori_url, detection.res_url])
    # detect_stream(detection.model_id, detection.id, detection.ori_url, detection.res_url)

    # created_task = celery_app.send_task("app.tasks.detection_task", args=[detection.model_id, detection.id, detection.ori_filename, detection.res_filename])
    
    #############
    # ori_image_path = os.path.join('./app/public', detection.ori_filename)
    # res_image_path = os.path.join('./app/public', detection.res_filename)
    # result = detect_image(detection.model_id, detection.id, ori_image_path, res_image_path)
    #############

    return detection

@r.post("/detections/{detection_id}")
async def detection_edit(
    detection_id: int,
    request: Request,
    detection: DetectionEdit,
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):
    return edit_detection(db, detection_id, detection)

from app.tasks import detect_image, detect_video
@r.post("/detections")
async def detection_create(
    request: Request,
    detection: DetectionCreate = Depends(DetectionCreate.as_form),
    image: UploadFile = File(...),
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):

    filename, file_extension = os.path.splitext(image.filename)
    # if detection.detection_type=='Video':
    #     file_extension = '.avi'
    new_filename = filename + '_res' + file_extension

    with open(os.path.join(static_dir, image.filename), "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    detection = create_detection(db, detection, image.filename, new_filename)

    created_task = celery_app.send_task("app.tasks.detection_task", args=[detection.model_id, detection.id, detection.ori_filename, detection.res_filename, detection.detection_type])
    
    #############
    # ori_image_path = os.path.join('./app/public', detection.ori_filename)
    # res_image_path = os.path.join('./app/public', detection.res_filename)
    # if detection.detection_type=='Image':
    #     result = detect_image(detection.model_id, detection.id, ori_image_path, res_image_path)
    # else:
    #     result = detect_video(detection.model_id, detection.id, ori_image_path, res_image_path)
    #############

    return detection

@r.get(
    "/detections/{detection_id}",
    response_model=Detection,
    response_model_exclude_none=True,
)
async def get_one_detection(
    detection_id: int,
    response: Response,
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):
    detection = get_detection(db, detection_id)
    return detection

@r.get(
    "/detections",
    response_model=t.List[Detection],
    response_model_exclude_none=True,
)
async def detections_list(
    response: Response,
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):
    """
    Get all detections
    """
    detections = get_detections(db)
    # This is necessary for react-admin to work
    response.headers["Content-Range"] = f"0-9/{len(detections)}"
    return detections

