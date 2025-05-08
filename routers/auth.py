from tokenize import Token

from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import BaseModel
from models import User
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime

router = APIRouter(
    prefix="/auth",        #bu da bağlantıya auth ya da todo ekler
    tags=["Authentication"], #büyük başlık
)

SECRET_KEY = "66r23mdtbjuavyyunqvqwe191r5h286bxte3o0jazfq5hket0rwryxt2ev5e135a"
ALGORIYHM = "HS256"



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=("bcrypt"), deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/togen")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    payload = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc)+expires_delta
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORIYHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
     try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORIYHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        user_role = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or ID is invalid")
        return {'username': username, 'id': user_id, 'user_role': user_role}
     except JWTError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token is invalid")

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        role=create_user_request.role,
        is_active=True,
        hashed_password=bcrypt_context.hash(create_user_request.password)

    )
    db.add(user)
    db.commit()


@router.post(path="/token", response_model=Token  )
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                  db: db_dependency):
     user = authenticate_user(form_data.username, form_data.password, db)
     if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
     token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
     return {"access_token": token, "token_type": "bearer"}











