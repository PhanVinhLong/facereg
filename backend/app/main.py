from fastapi import FastAPI, Depends
from starlette.requests import Request
import uvicorn

from fastapi.middleware.cors import CORSMiddleware  

from fastapi.responses import UJSONResponse

from app.core import config
from app import tasks

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from fastapi.responses import FileResponse
import os
from fastapi.staticfiles import StaticFiles

#---------------------------------------

from fastapi import APIRouter, Request, Response, encoders, File, UploadFile, Form, BackgroundTasks
import typing as t
import io
from starlette.responses import StreamingResponse
import torch

import shutil
import os
import json
import sys
import time
import uuid
import random
import cv2
from PIL import Image

import sys
sys.path.append("./app/InsightFace")
from arcface import Recognition

recognition = Recognition()

app = FastAPI(
    title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate():
    while recognition.cap.isOpened():
        ret, img = recognition.cap.read()
        if ret == True:
            img = recognition.draw_min_face(img)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(img) + b'\r\n')
        else:
            pass

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = await call_next(request)
    return response

@app.get("/api/v1/feed")
def video_feed(
    request: Request,
):
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.post("/api/v1/update_facebank")
async def update_facebank(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str,
    files: t.List[UploadFile] = File(...)
):
    recognition.update_facebank(files, url)

@app.get("/api/v1/recognize_image/{tmp}")
def get_result_image(
    request: Request,
):
    result, image = recognition.cap_and_draw_min_face()
    if(not(result)):
        return Response(status_code=501)
    else:
        return StreamingResponse(io.BytesIO(image.tobytes()), media_type="image/png")

@app.get('/info', tags=['Utility'])
def info():
    """
    Enslist container configuration.
    """

    about = dict(
        version=__version__,
        tensorrt_version=os.getenv('TRT_VERSION', os.getenv('TENSORRT_VERSION')),
        log_level=configs.log_level,
        models=vars(configs.models),
        defaults=vars(configs.defaults),
    )
    about['models'].pop('ga_ignore', None)
    about['models'].pop('rec_ignore', None)
    about['models'].pop('device', None)
    return about


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url='/static/favicon.png'
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8888)
