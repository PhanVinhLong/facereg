#!/usr/bin/env python3

from app.db.session import get_db
from app.db.crud import create_user, create_model
from app.db.schemas import UserCreate, ModelCreate
from app.db.session import SessionLocal, Base, engine


def init() -> None:
    db = SessionLocal()

    Base.metadata.create_all(bind=engine)

    create_user(
        db,
        UserCreate(
            email="longpv.se@gmail.com",
            password="123456",
            is_active=True,
            is_superuser=True,
        ),
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-init",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="Initial YOLOv4 model using default hyperparameters",
            input_width=416,
            input_height=416,
            weight_size=255
        )
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-r",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="YOLOv4 model changed input size (ratio)",
            input_width=544,
            input_height=320,
            weight_size=255
        )
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-a",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="YOLOv4 model changed anchor boxes",
            input_width=416,
            input_height=416,
            weight_size=255
        )
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-s",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="YOLOv4 model changed input size (increase size)",
            input_width=512,
            input_height=512,
            weight_size=255
        )
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-n",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="YOLOv4 model changed network structure",
            input_width=416,
            input_height=416,
            weight_size=255
        )
    )

    create_model(
        db,
        ModelCreate(
            name="YOLOv4-final",
            is_active=True,
            model_type="YOLOv4 pytorch",
            created_time="2020-12-01T15:53:00+08:00",
            description="YOLOv4 model combine all optimizations",
            input_width=672,
            input_height=384,
            weight_size=255
        )
    )


if __name__ == "__main__":
    print("Initiating data...")
    init()
    print("Data created")
