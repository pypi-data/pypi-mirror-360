# my_ai_lib/db_connector.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

class DatabaseConnector:
    """
    Класс для управления подключениями к внешним базам данных пользователей.
    Поддерживает различные типы реляционных СУБД (SQLite, PostgreSQL).
    """

    def __init__(self, db_type: str, connection_string: str):
        """
        Инициализирует коннектор к базе данных.

        Args:
            db_type (str): Тип базы данных (например, 'sqlite', 'postgresql', 'mysql').
                           Влияет на выбор драйвера и формат строки подключения.
            connection_string (str): Строка подключения к базе данных.
                                     Примеры:
                                     - SQLite: 'sqlite:///path/to/your/database.db'
                                     - PostgreSQL: 'postgresql+psycopg2://user:password@host:port/database_name'
                                     - MySQL: 'mysql+mysqlconnector://user:password@host:port/database_name'
        Raises:
            ValueError: Если указан неподдерживаемый тип базы данных.
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal: Optional[sessionmaker] = None

        self._initialize_engine()

    def _initialize_engine(self):
        """
        Создает движок SQLAlchemy на основе типа и строки подключения.
        """
        if self.db_type == 'sqlite':
            # Для SQLite, connection_string уже должна быть в формате 'sqlite:///path/to/db.db'
            self.engine = create_engine(self.connection_string, connect_args={"check_same_thread": False})
        elif self.db_type == 'postgresql':
            # Для PostgreSQL нужен psycopg2 или другой драйвер
            # Убедитесь, что connection_string включает 'postgresql+psycopg2://'
            self.engine = create_engine(self.connection_string, pool_pre_ping=True)
        # elif self.db_type == 'mysql':
        #     # Для MySQL нужен mysql-connector-python или pymysql
        #     # Убедитесь, что connection_string включает 'mysql+mysqlconnector://' или 'mysql+pymysql://'
        #     self.engine = create_engine(self.connection_string, pool_pre_ping=True)
        else:
            raise ValueError(f"Неподдерживаемый тип базы данных: {self.db_type}. Поддерживаются 'sqlite', 'postgresql'.")

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print(f"Движок БД для {self.db_type} успешно инициализирован.")

    def get_session(self) -> Session:
        """
        Возвращает новую сессию SQLAlchemy для взаимодействия с базой данных.
        Сессию следует закрыть после использования, используя 'with' statement.
        Пример: with connector.get_session() as session: ...

        Raises:
            RuntimeError: Если движок БД не был инициализирован.
        """
        if not self.SessionLocal:
            raise RuntimeError("Движок базы данных не инициализирован. Вызовите _initialize_engine().")
        
        try:
            session = self.SessionLocal()
            return session
        except SQLAlchemyError as e:
            raise RuntimeError(f"Ошибка при создании сессии БД: {e}")

    def test_connection(self) -> bool:
        """
        Проверяет соединение с базой данных.
        """
        if not self.engine:
            print("Соединение не инициализировано.")
            return False
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1")) # Простая тестовая команда
            print(f"Соединение с {self.db_type} БД успешно установлено.")
            return True
        except SQLAlchemyError as e:
            print(f"Ошибка соединения с {self.db_type} БД: {e}")
            return False

# Пример использования в __main__ для тестирования
if __name__ == "__main__":
    print("Тестирование DatabaseConnector...")

    # --- Тестирование SQLite ---
    sqlite_db_path = 'test_restaurant.db' # Используем нашу ранее созданную тестовую БД
    sqlite_conn_string = f'sqlite:///{sqlite_db_path}'
    try:
        sqlite_connector = DatabaseConnector(db_type='sqlite', connection_string=sqlite_conn_string)
        sqlite_connector.test_connection() # Эта строка вызывает execute("SELECT 1")

        # Пример использования сессии
        with sqlite_connector.get_session() as session:
            # Для реальных запросов здесь потребуются модели или text() из sqlalchemy
            # Используем text() для сырых SQL-запросов
            # Исправляем SELECT 1 в test_connection() косвенно, поскольку он использует тот же механизм
            result = session.execute(text("SELECT name FROM restaurant_info LIMIT 1")).scalar_one() # <--- ИСПРАВЛЕНО
            print(f"Получено из SQLite: {result}")

    except ValueError as e:
        print(f"Ошибка конфигурации SQLite: {e}")
    except RuntimeError as e:
        print(f"Ошибка во время выполнения SQLite запроса: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при работе с SQLite: {e}")

    print("\n--- Тестирование PostgreSQL (требует запущенного сервера PostgreSQL и psycopg2-binary) ---")
    # ЗАМЕНИТЕ НА ВАШИ ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ!
    postgresql_conn_string = 'postgresql+psycopg2://user:password@localhost:5432/mydatabase' 
    try:
        pg_connector = DatabaseConnector(db_type='postgresql', connection_string=postgresql_conn_string)
        # Здесь также нужно обернуть "SELECT 1" в test_connection() в text()
        pg_connector.test_connection()
        # Попробуйте выполнить простой запрос
        # with pg_connector.get_session() as session:
        #    result = session.execute(text("SELECT version();")).scalar_one() # <--- Пример, если будете тестировать
        #    print(f"Получено из PostgreSQL: {result}")
    except ValueError as e:
        print(f"Ошибка конфигурации PostgreSQL: {e}")
    except RuntimeError as e:
        print(f"Ошибка во время выполнения PostgreSQL запроса: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при работе с PostgreSQL: {e}. Возможно, не установлен 'psycopg2-binary' или сервер не запущен.")