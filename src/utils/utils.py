from datetime import datetime

from src.data.engine import SessionLocal
from src.data.models import User, Date

from typing import List, Dict
from passlib.context import CryptContext



#Добавление пользователя в БД
def create_user(login: str, password: str):
    session = SessionLocal() #Создаем соединение с бд
    try:
        user = User(login=login, hash_password=hash_password(password)) #Подготавливаем данные для записи
        session.add(user) #Записываем данные
        session.commit() #Проверяем попали ли данные
        session.refresh(user) # обновляем данные
        print("Пользователь создан:", user.login)
    except Exception as e:
        session.rollback()
        print("Ошибка:", e)
    finally:
        session.close() #Закрываем соединение


#Проверка на существование пользователя
def get_user_by_login(login: str):
    session = SessionLocal() #Создаем соединение
    try:
        user = session.query(User).filter(User.login == login).first() #Создаем запрос в таблицу User => Фильтруем по полю логин и проверяем на совпадение

        if user:
            print("Найден пользователь:", user.login)
            return user
        else:
            print("Пользователь не найден")
            return False
    finally:
        session.close()




#Функция для выдачи сессии после запуска сервера
def give_session(user: str, sessions: List[Dict]) -> int:
    # Проверяем существующие сессии пользователя
    if sessions:
        for session in sessions:
            if session["user"] == user:
                return session["session_id"]

        # Генерируем новый session_id
        new_id = sessions[-1]["session_id"] + 1

        # Добавляем новую сессию
        sessions.append({
            "user": user,
            "session_id": new_id, # Добавляем недостающее поле
            "is_active": True
        })
        return new_id
    else:
        sessions.append({
            "user": user,
            "session_id": 0,
            "is_active": True
        })
        return 0


def add_reminderdb(year: int, month: int, day: int, reminder: list, user: str):
    date = datetime(year, month, day)

    # Собираем напоминания в одну строку с переносами строк
    remind = "\n".join([f"{i}) {r}" for i, r in enumerate(reminder, 1)])

    session = SessionLocal()
    try:
        # Проверка: есть ли уже запись для этой даты и пользователя
        existing = session.query(Date).filter_by(login=user, date=date).first()

        if existing:
            # Обновляем напоминание
            existing.reminder = remind
            print("Напоминание обновлено")
        else:
            # Создаём новое
            date_ = Date(login=user, date=date, reminder=remind)
            session.add(date_)
            print("Напоминание создано")

        session.commit()
        return remind

    except Exception as e:
        session.rollback()
        print("Ошибка при работе с БД:", e)
    finally:
        session.close()




def is_valid_session(session_id: str, sessions: list[dict]) -> bool:
    try:
        session_id_int = int(session_id)
        return any(
            session["session_id"] == session_id_int
            and session["is_active"]
            for session in sessions
        )
    except (ValueError, KeyError):
        return False




def get_reminderdb(year: int, month: int, day: int, user: str):
    date = datetime(year, month, day)
    session = SessionLocal()
    try:
        reminders = (
            session.query(Date).filter(Date.login == user, Date.date == date).all()
        )
        return reminders
    finally:
        session.close()


#Объект для работы с паролем
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#Создание хешпароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


#Проверка пароля по ранее созданному хешу
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)