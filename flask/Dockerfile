FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /flask

COPY requirements.txt /flask/requirements.txt
RUN pip install -r requirements.txt

COPY app /flask/app
COPY wsgi.py /flask/wsgi.py

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--access-logfile=access.log", "--error-logfile=error.log", "wsgi:app"]
