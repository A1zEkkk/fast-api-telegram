import os

from dotenv import load_dotenv

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

#Генератор URL
url_obj = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="postgres",
    host="localhost",
    database="postgres",
    port=5433
)



#Соединение с базой данных
engine = create_engine(url_obj, echo=True)
#Класс для создания сессий и подключение к бд
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
