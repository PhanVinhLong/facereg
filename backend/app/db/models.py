from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_time = Column(DateTime)
    description = Column(String)
    input_width = Column(Integer)
    input_height = Column(Integer)
    weight_size = Column(Integer)
    model_type = Column(String)

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    detection_type = Column(String)
    model_id = Column(Integer)
    created_time = Column(DateTime)
    created_by = Column(String)
    status = Column(String)
    description = Column(String)
    ori_filename = Column(String)
    res_filename = Column(String)
    process_time = Column(Integer)
    results = Column(String)
    