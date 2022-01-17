#setup uwsgi and app
FROM python:2 as blog

RUN apt-get update && \
    apt-get install -y build-essential python vim net-tools && \
    pip install uwsgi

WORKDIR /
COPY . /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD [ "uwsgi", "--ini", "/app/uwsgi.ini" ]