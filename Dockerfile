# 1. Базовый образ с Python
FROM python:3.13-slim

# 2. Не писать .pyc и сразу логировать в stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Рабочая директория в контейнере
WORKDIR /app

# 4. Устанавливаем зависимости
# Если у тебя есть requirements.txt — можно поставить так:
# COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt

# Если зависимостей немного, можно пока в лоб:
RUN pip install --upgrade pip \
    && pip install fastapi uvicorn[standard] sqlalchemy pydantic psycopg2-binary pyjwt cryptography requests

# 5. Копируем код сервиса внутрь контейнера
COPY app ./app

# 6. Открываем порт (для читаемости, не обязательно)
EXPOSE 8000

# 7. Команда запуска FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
