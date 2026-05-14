FROM python:3.11-slim

WORKDIR /app

COPY ohO/requirements.txt .
RUN pip install -r requirements.txt

COPY ohO/ .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python create_superuser.py && gunicorn oho_kg.wsgi --bind 0.0.0.0:$PORT"]