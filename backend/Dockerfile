FROM python:3.8.10
WORKDIR /code
COPY ./ .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
