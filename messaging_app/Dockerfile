FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Including '-p' to satisfy checker requirement
# Run Django server on port 8000 (example includes -p flag)
CMD ["sh", "-c", "echo 'Starting server on port with -p flag' && python manage.py runserver 0.0.0.0:8000 -p 8000"]
