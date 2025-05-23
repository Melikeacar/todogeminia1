from sys import prefix

from fastapi import APIRouter, Depends, Path, HTTPException, Security
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated
from routers.auth import get_current_user


router = APIRouter(
    prefix="/todo",
    tags=["Todo"],
)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]


@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found" )


@router.post(path="/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = Todo(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo)
    db.commit()    # bu commit add den sonra işlemin yapılacağı anlamına gelir . bunu eklemezsek ekleme yapmaz.


@router.put(path="/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()


@router.delete(path="/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.query(Todo).filter(Todo.id == todo_id).delete() ##bu olmasada olur çalışırı. olmasının sebebi silme işleminden emin olmak
    db.delete(todo)
    db.commit()
#burada delete kısmını id den yapmak en iyi olan bir veri silinirse id den silinsin diye
#not : kullanıcı filtrelmesiyle daha güvenli uygulama yapmak kısmını aç verileri db ye girmeye çalış
