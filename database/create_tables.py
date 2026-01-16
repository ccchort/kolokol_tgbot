from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base
from config import config

# Конфигурация PostgreSQL
DB_CONFIG = {
    "protocol": "postgresql+asyncpg",
    "user": config.postgres_user.get_secret_value(),
    "password": config.postgres_password.get_secret_value(),
    "host": config.postgres_host.get_secret_value(),
    "port": config.postgres_port.get_secret_value(),
    "db_name": config.postgres_db.get_secret_value()
}



# Настройка подключения к базе данных
protocol = "postgresql+psycopg2-binary"
username = DB_CONFIG.get("user")  # 🔹 Логин от PostgreSQL
password = DB_CONFIG.get("password")  # 🔹 Пароль от PostgreSQL
server = DB_CONFIG.get("host")    # 🔹 Например, localhost или IP
port = DB_CONFIG.get("port")              # 🔹 Порт (по умолчанию 5432)
database = DB_CONFIG.get("db_name")  # 🔹 Название базы данных

connection_string = f"{protocol}://{username}:{password}@{server}:{port}/{database}"
print(connection_string)

# Создание движка для подключения к базе данных
engine = create_engine(connection_string)

# Создание таблиц
Base.metadata.create_all(bind=engine)
