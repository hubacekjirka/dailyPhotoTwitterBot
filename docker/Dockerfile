### Base stage
FROM ubuntu:20.04 as base

RUN apt-get update
RUN apt-get install -y python3.8-dev python3-pip gcc 

CMD mkdir -p /app/src

WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt

### Copy code stage
FROM base as code
WORKDIR /app
COPY . /app

### Production stage
WORKDIR /app/src
FROM code as prod
CMD ["python3", "bot.py"]