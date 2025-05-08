from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from models import Base, Todo
from database import engine
from routers.auth import router as auth_router
from routers.todo import router as todo_router
from fastapi.staticfiles import StaticFiles
from starlette import status

app = FastAPI()

app.mount(path="/static", app=StaticFiles(directory="static"), name="static")



@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTT_302_FOUND)


app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)  #bu database main de kalmalı






    
