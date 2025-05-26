FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt --break-system-packages
