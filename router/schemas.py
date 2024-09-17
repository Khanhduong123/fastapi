from pydantic import BaseModel, Field


class TodosRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=0, lt=6)
    complete: bool


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class UserVerify(BaseModel):
    password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
