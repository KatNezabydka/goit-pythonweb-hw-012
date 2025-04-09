from datetime import date
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactModel(BaseModel):
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    birthday: date | None = Field(None)
    additional_info: str | None = Field(None, max_length=255)


model_config = ConfigDict(from_attributes=True)


class ContactUpdate(ContactModel):
    pass


class ContactResponse(ContactModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: EmailStr
