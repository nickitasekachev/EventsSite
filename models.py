from sqlalchemy import Column, Integer, Float, Date, DateTime, Text, Boolean, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, query_expression
from sqlalchemy.sql import func
from database import Base, db_session, engine as db_engine
import datetime
from flask_login import UserMixin

class Sponsor(Base):
    __tablename__ = "sponsors"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="")
    logo = Column(String(100), nullable=False, default="")
    description = Column(String(300))  # Описание компании
    kpp = Column(String(20))  # КПП
    inn = Column(String(20))  # ИНН
    office_address = Column(String(500))  # Адрес офиса
    # Другие поля, если необходимо

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    photo = Column(String(100), nullable=False, default="")
    full_name = Column(String(150), nullable=False, default="")
    position_and_company = Column(String(500), nullable=False, default="")
    phone_number = Column(String(20), nullable=False, default="")
    # Другие поля, если необходимо

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, default="")
    surname = Column(String(200), nullable=False, default="")
    phone_number = Column(String(100), nullable=False, default="")
    mail = Column(String(200), nullable=False, default="")
    addres = Column(String(200), nullable=False, default="")
    login = Column(String(100), unique=True)
    password = Column(String(200))

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, default="")
    photo = Column(String(200), nullable=False, default="")
    date_time = Column(DateTime, nullable=False)
    description = Column(String(300))  # Краткое описание
    restrictions = Column(String(300))  # Информация о возможных ограничениях
    registration_required = Column(Boolean, default=False)  # Признак необходимости предварительной регистрации
    detailed_info = Column(String(500))  # Подробная информация о мероприятии
    location = Column(String(500))  # Место проведения (адрес)
    # Другие поля, если необходимо
    event_info_name = Column(String(200), ForeignKey('event_info.name'))  # Внешний ключ для связи с именем EventInfo
    event_info = relationship("EventInfo", back_populates="events")  # Отношение "один-ко-многим"
    participants = relationship('UserEvent', back_populates='event')  # Связь с участниками

class EventInfo(Base):
    __tablename__ = "event_info"
    name = Column(String(200), primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    city = Column(String(200), nullable=False, default="")
    address = Column(String(500), nullable=False, default="")
    main_phone = Column(String(20), nullable=False, default="")
    email = Column(String(200), nullable=False, default="")
    social_link_1 = Column(String(100))
    social_link_2 = Column(String(100))
    social_link_3 = Column(String(100))
    # Другие поля, если необходимо
    events = relationship("Event", back_populates="event_info")

class UserEvent(Base):
    __tablename__ = 'user_events'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    user = relationship('User', back_populates='events')
    event = relationship('Event', back_populates='participants')

User.events = relationship('UserEvent', back_populates='user')

def init_db():
    from database import engine
    Base.metadata.create_all(bind=engine)
    db_session.commit()

def print_schema(table_class):
    from sqlalchemy.schema import CreateTable, CreateColumn
    print(str(CreateTable(table_class.__table__).compile(db_engine)))

def print_columns(table_class, *attrNames):
   from sqlalchemy.schema import CreateTable, CreateColumn
   c = table_class.__table__.c
   print( ',\r\n'.join((str( CreateColumn(getattr(c, attrName)).compile(db_engine)) \
                            for attrName in attrNames if hasattr(c, attrName)
               )))

if __name__ == "__main__":
    init_db()
