from pydantic import BaseModel
#Файл для хранения антаторов


class UserCreate(BaseModel):
    login: str
    password: str

class YMD(BaseModel):
    years: int
    month: int
    day:   int