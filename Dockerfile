FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir fastapi uvicorn pyjwt pycryptodome pydantic python-multipart pydantic[email] requests cryptography redis sqlalchemy psycopg2-binary passlib[argon2]
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host","0.0.0.0", "--port","8000"]
