#setup uwsgi and app
FROM python:3 as blog

RUN apt-get update && \
    apt-get install -y build-essential python vim net-tools && \
    pip3 install uwsgi

WORKDIR /
COPY . /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt
EXPOSE 8000
CMD [ "uwsgi", "--ini", "/app/blog_uwsgi.ini" ]
