from pydantic import BaseModel
import typing as t
import inspect
from fastapi import Form
import datetime

def as_form(cls: t.Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False
    first_name: str = None
    last_name: str = None


class UserOut(UserBase):
    pass


class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserEdit(UserBase):
    password: t.Optional[str] = None

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
    permissions: str = "user"

class ModelBase(BaseModel):
    name: str
    is_active: bool = True
    created_time: datetime.datetime
    description: str
    input_width: int
    input_height: int
    weight_size: int
    model_type: str

class ModelCreate(ModelBase):

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "name": "YOLOv4 pytorch",
                "is_active": True,
                "created_time": "2020-12-01T15:53:00+08:00",
                "description": "Initial YOLOv4 model using default hyperparameters",
                "input_width": 416,
                "input_height": 416,
                "weight_size": 255,
                "model_type": "YOLOv4 pytorch"
            }
        }

class Model(ModelBase):
    id: int

    class Config:
        orm_mode = True

class DetectionBase(BaseModel):

    name: t.Optional[str]
    detection_type: t.Optional[str]
    model_id: t.Optional[int]
    created_time: t.Optional[datetime.datetime]
    created_by: t.Optional[str]
    status: t.Optional[str]
    description: t.Optional[str]
    ori_url: t.Optional[str]

@as_form
class DetectionCreate(DetectionBase):

    class Config:
        orm_mode = True

class DetectionEdit(DetectionBase):

    results: t.Optional[str]

    class Config:
        orm_mode = True

class Detection(DetectionBase):
    id: int
    ori_filename: t.Optional[str]
    res_filename: t.Optional[str]
    res_url: t.Optional[str]
    process_time: t.Optional[int]
    results: t.Optional[str]

    class Config:
        orm_mode = True
