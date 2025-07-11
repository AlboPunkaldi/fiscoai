from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr, Field as PydField
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True)
    role: str = Field(default="user")  # user | admin

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = PydField(min_length=8)

    @staticmethod
    def hash_pw(password: str) -> str:
        return pwd_ctx.hash(password)