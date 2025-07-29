# my_ai_lib_project/my_ai_lib/db_manager.py


from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os
from typing import Optional

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_user_id = Column(String(255), nullable=False, index=True) 
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.timestamp")
    agent = relationship("Agent", back_populates="sessions") # <--- ДОБАВЬТЕ ЭТУ СТРОКУ

    def __repr__(self):
        return f"<ChatSession(id='{self.id}', client_user_id='{self.client_user_id}', agent_id='{self.agent_id}')>"

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=False)
    sender = Column(String(50), nullable=False) # 'user' или 'ai'
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id='{self.id}', sender='{self.sender}', timestamp='{self.timestamp}')>"

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(UUID(as_uuid=True), primary_key=True) # ID агента из DeepForge (совпадает с его ключом)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    sessions = relationship("ChatSession", back_populates="agent")

    def __repr__(self):
        return f"<Agent(id='{self.id}', name='{self.name}', company_name='{self.company_name}')>"


class DatabaseManager:
    def __init__(self, connection_string: Optional[str] = None): # <--- ИЗМЕНЕНИЕ ЗДЕСЬ!
        """
        Инициализирует менеджер базы данных.

        Args:
            connection_string: Строка подключения к базе данных SQLAlchemy.
                               По умолчанию используется SQLite: 'sqlite:///chat_history.db'
                               Примеры:
                               - PostgreSQL: 'postgresql://user:password@host:port/dbname'
                               - MySQL: 'mysql+mysqlconnector://user:password@host:port/dbname'
                               - Oracle: 'oracle+cx_oracle://user:password@host:port/dbname'
        """
        if connection_string is None:
            # Дефолтное значение: SQLite-файл в текущей директории
            self.connection_string = 'sqlite:///chat_history.db'
            print(f"Используется БД по умолчанию (SQLite): {self.connection_string}")
        else:
            self.connection_string = connection_string
            print(f"Используется пользовательская БД: {self.connection_string}")

        self.engine = create_engine(self.connection_string) # <--- ИЗМЕНЕНИЕ ЗДЕСЬ!
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        Создает все таблицы в базе данных, если они еще не существуют.
        """
        Base.metadata.create_all(self.engine)
        print(f"База данных и таблицы успешно созданы или уже существуют: {self.connection_string}")

    def get_session(self):
        """
        Возвращает новую сессию базы данных.
        """
        return self.Session()