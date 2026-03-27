import os, base64, bcrypt, models
from fastapi import APIRouter, Depends, HTTPException, status, security
from pydantic import BaseModel, Field
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from database import db_dependency



router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
oauth = security.OAuth2PasswordRequestForm
bearer = security.OAuth2PasswordBearer(tokenUrl='/auth/token')
# openssl rand -hex 32
HEX_STR = 'b23cd44757667b58783ca20522a86de09c4bd7cf9c3ddfb738687cdffd35a6ef'
SK = os.getenv("SK", HEX_STR)
key = bytes.fromhex(SK)
ALGO = 'HS256'

b64_str = base64.b64encode(key).decode('utf-8')
b64url_str = base64.urlsafe_b64encode(key).decode('utf-8').rstrip('=')




async def auth(username: str, password: str, db: db_dependency):
    statement = select(models.Users).filter(models.Users.username == username)
    result = await db.execute(statement)
    user = result.scalars().first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return False
    return user

async def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    claims = {'sub': username, 'id': user_id, 'role': role, 'exp': expires}
    return jwt.encode(claims, key, algorithm=ALGO)

async def get_current_user(token: Annotated[str, Depends(bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, key, algorithms=[ALGO])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "id": user_id, "role": role}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=1, max_length=256)
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=256)
    role: Optional[str] = Field(default="user", min_length=1, max_length=256)   




@router.post("/signup")
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    
    statement = select(models.Users).filter(models.Users.email == create_user_request.email)
    result = await db.execute(statement)
    userCheck = result.scalars().first()
    if userCheck:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    statement = select(models.Users).filter(models.Users.username == create_user_request.username)
    result = await db.execute(statement)
    userCheck = result.scalars().first()
    if userCheck:
        raise HTTPException(status_code=400, detail="User with this username already exists")

    # hpw = bcrypt.hashpw(encoded_pw, salt)
    hashed_pw = bcrypt.hashpw(create_user_request.password.encode("utf-8"), bcrypt.gensalt())

    user = models.Users(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=hashed_pw.decode("utf-8"),
        role=create_user_request.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User created successfully", "user": user}


@router.post("/login")
async def login(form_data: Annotated[oauth, Depends()], db: db_dependency):
    print("Attempting login for user:", form_data.username)
    user = await auth(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return {"message": "login successful", "access_token":  token, "token_type": "bearer"}
