from fastapi import FastAPI, Depends
from starlette.requests import Request
import uvicorn

from fastapi.middleware.cors import CORSMiddleware  

from app.api.api_v1.routers.users import users_router
from app.api.api_v1.routers.auth import auth_router
from app.api.api_v1.routers.models import models_router
from app.api.api_v1.routers.faces import faces_router
from app.api.api_v1.routers.detections import detections_router

from torch.multiprocessing import Pool, Process, set_start_method

from app.core import config
from app.db.session import SessionLocal
from app.core.auth import get_current_active_user
# from app.core.celery_app import celery_app
from app import tasks

from fastapi.responses import FileResponse
import os
from fastapi.staticfiles import StaticFiles

static_dir = "./app/public"

try:
    set_start_method('spawn')
except RuntimeError:
    pass

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

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response

app.mount("/api/files", StaticFiles(directory="./app/public"), name="files")

@app.get("/api/files/{filename}")
async def get_file(filename: str):
    return FileResponse(os.path.join(static_dir, filename))

@app.get("/api/file/{filename}")
async def get_files(filename: str):

    if not os.path.isdir(static_dir):
        return {"result": "empty"}

    _, _, filenames = next(os.walk(static_dir))
    
    if len(filenames) == 0:
        return {"result": "empty"}

    return FileResponse(os.path.join(static_dir, filenames[0]))

@app.get("/api/v1")
async def root():
    return {"message": "Hi World2"}

# @app.get("/api/v1/task")
# async def example_task():
#     celery_app.send_task("app.tasks.example_task", args=["Hello World"])

#     return {"message": "success"}

# Routers
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["users"],
    # dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    models_router,
    prefix="/api/v1",
    tags=["models"],
    # dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    faces_router,
    prefix="/api/v1",
    tags=["faces"],
    # dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    detections_router,
    prefix="/api/v1",
    tags=["detections"],
    # dependencies=[Depends(get_current_active_user)],
)
app.include_router(auth_router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8888)
