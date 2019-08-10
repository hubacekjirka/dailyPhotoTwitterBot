FROM ubuntu:18.04

# RUN apk --update add gcc libgcc musl-dev
# RUN apk add jpeg-dev zlib-dev
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip gcc 

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

# Download Tensorflow model
WORKDIR /app/src
RUN python3 classify_image.py

CMD ["/bin/sh"]