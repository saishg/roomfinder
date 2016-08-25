FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
ENV PYTHONPATH $PYTHONPATH:/app/roomfinder
RUN pip install Flask==0.10.1
ENTRYPOINT ["python"]
CMD ["service/webserver.py"]
