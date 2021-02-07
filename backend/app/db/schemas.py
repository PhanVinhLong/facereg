from pydantic import BaseModel
import typing as t
import datetime

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
