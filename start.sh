#!/bin/bash
# Замени 'ffllaapp' на фактическое имя папки твоего репозитория, когда склонируешь его в Replit!
cd ffllaapp 

export PORT=5000
unset PIP_USER

# Создание venv, если его нет
if [ ! -d "venv" ]; then
 echo "Creating virtual environment..."
 python3 -m venv venv --system-site-packages
fi

# Активация окружения
source venv/bin/activate

# Установка зависимостей
if [ -f "requirements.txt" ]; then
 echo "Checking dependencies..."
 pip install -r requirements.txt
fi

echo "Starting application..."
# Запуск Streamlit на нужном для Replit порту
streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
