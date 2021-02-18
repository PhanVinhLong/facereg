from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import typing as t

from . import models, schemas
from app.core.security import get_password_hash

# users

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str) -> schemas.UserBase:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.UserOut]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return user


def edit_user(
    db: Session, user_id: int, user: schemas.UserEdit
) -> schemas.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(user.password)
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_models(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.Model]:
    return db.query(models.Model).offset(skip).limit(limit).all()

def create_model(db: Session, model: schemas.ModelCreate):
    db_model = models.Model(
        name = model.name,
        is_active = model.is_active,
        created_time = model.created_time,
        description = model.description,
        input_width = model.input_width,
        input_height = model.input_height,
        weight_size = model.weight_size,
        model_type = model.model_type
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_detections(
    db: Session, skip: int = 0, limit: int = 100
) -> t.List[schemas.Detection]:
    return db.query(models.Detection).offset(skip).limit(limit).all()

def create_detection(db: Session, detection: schemas.DetectionCreate, ori_filename: str, res_filename: str):
    db_detection = models.Detection(
        name = detection.name,
        detection_type = detection.detection_type,
        model_id = detection.model_id,
        created_time = detection.created_time,
        created_by = detection.created_by,
        status = detection.status,
        description = detection.description,
        ori_filename = ori_filename,
        res_filename = res_filename
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection
