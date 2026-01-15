# Используем официальный Python образ
FROM python:3.11.9

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем файл с кодом бота
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
