from models import Users
from .schemas import UserVerify
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi import Depends, APIRouter, HTTPException, status, Path
from .auth import get_current_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    try:
        if user is not None and user.get("user_role") == "admin":
            return db.query(Users).all()
        else:
            return db.query(Users).filter(Users.id == user["id"]).first()
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, user_vertify: UserVerify
):

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    user_models = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_vertify.password, user_models.hashed_password):
        raise HTTPException(status_code=401, detail="Password not match")

    user_models.hashed_password = bcrypt_context.hash(user_vertify.new_password)
    db.add(user_models)
    db.commit()
