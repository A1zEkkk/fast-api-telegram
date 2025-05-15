from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from src.handlers.auth import router1
from src.handlers.dashboard import router2
from src.handlers.root import router3

app = FastAPI()



# Для браузера
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Инициализируем шаблонизатор
templates = Jinja2Templates(directory="frontend/templates")


# Подключаем роутеры
app.include_router(router1, tags=["Authentication"])
app.include_router(router2, tags=["Dashboard"])
app.include_router(router3)