FROM python:3.12

RUN mkdir /app

WORKDIR /app

# so python does not write pyc files to disk and runs unbuffered IO
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# TODO: change for WSGI server
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
