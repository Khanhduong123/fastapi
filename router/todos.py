import models
from models import Todos
from router.schemas import TodosRequest
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi import Depends, APIRouter, HTTPException, status, Path
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    return db.query(Todos).filter(Todos.owner_id == user["id"]).all()


@router.get("/part3/{id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    todo_models = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.owner_id == user["id"])
        .first()
    )

    if todo_models is not None:
        return todo_models
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/part3/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodosRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user["id"])
    db.add(todo_model)
    db.commit()


@router.put("/part3/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodosRequest,
    id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.owner_id == user["id"])
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/part3/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.owner_id == user["id"])
        .first()
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user["id"]).delete()
    db.commit()
