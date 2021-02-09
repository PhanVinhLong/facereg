from fastapi import APIRouter, Request, Depends, Response, encoders
import typing as t

from app.db.session import get_db
from app.db.crud import (
    get_models,
    create_model
)
from app.db.schemas import ModelCreate, Model
from app.core.auth import get_current_active_user, get_current_active_superuser

models_router = r = APIRouter()

@r.post("/models", response_model=Model, response_model_exclude_none=True)
async def model_create(
    request: Request,
    model: ModelCreate,
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):
    """
    Create a new model
    """
    return create_model(db, model)

@r.get(
    "/models",
    response_model=t.List[Model],
    response_model_exclude_none=True,
)
async def models_list(
    response: Response,
    db=Depends(get_db),
    # current_user=Depends(get_current_active_superuser),
):
    """
    Get all models
    """
    models = get_models(db)
    # This is necessary for react-admin to work
    response.headers["Content-Range"] = f"0-9/{len(models)}"
    return models

