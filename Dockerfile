#setup uwsgi and app
FROM python:3 as blog

RUN apt-get update && \
    apt-get install -y build-essential python vim net-tools && \
    pip3 install uwsgi

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt
EXPOSE 8000
#CMD ["ls", "-l"]
CMD [ "sh", "-c", "sleep 60 && python3 manage.py collectstatic --noinput && python3 manage.py search_index --rebuild -f && uwsgi --ini /app/blog_uwsgi.ini" ]
#CMD ["./wait-for-it.sh", "elasticsearch:9200", "--", "uwsgi", "--ini", "/app/blog_uwsgi.ini", "&&", "python3", "manage.py", "search_index", "--rebuild"]
