# Используем легкий образ Python
FROM python:3.11-slim

# Устанавливаем системные библиотеки прямо в систему Linux
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем библиотеки Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Команда запуска (Railway сам подставит PORT)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}