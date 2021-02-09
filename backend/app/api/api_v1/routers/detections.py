from fastapi import APIRouter, Request, Depends, Response, encoders, File, UploadFile, Form
import typing as t

from app.db.session import get_db
from app.db.crud import (
    get_detections,
    create_detection
)
from app.db.schemas import DetectionCreate, Detection
from app.core.auth import get_current_active_user, get_current_active_superuser

import shutil
import os

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

@r.post("/detections")
async def detection_create(
    request: Request,
    detection: DetectionCreate = Depends(DetectionCreate.as_form),
    image: UploadFile = File(...),
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):

    filename, file_extension = os.path.splitext(image.filename)
    new_filename = filename + '_res' + file_extension

    with open(image.filename, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {"filename": image.filename}

    return create_detection(db, detection)

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

