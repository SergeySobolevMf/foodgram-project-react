FROM python:3.7-slim

WORKDIR /foodgram


COPY requirements.txt /foodgram

RUN pip3 install -r /foodgram/requirements.txt --no-cache-dir

COPY . /foodgram


CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 