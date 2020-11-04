### Base stage
FROM ubuntu:18.04 as base

RUN apt-get update
RUN apt-get install -y python3.7-dev python3-pip gcc 

CMD mkdir -p /app/src

WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt

### Copy code stage
FROM base as code
WORKDIR /app
COPY . /app

# Download Tensorflow model
WORKDIR /app/src
RUN python3 classify_image.py

# Boot into the command shell
#CMD ["/bin/sh"]

### Production stage
FROM code as prod
CMD ["python3", "bot.py"]

### Debugging stage
FROM code as debug
RUN pip3 install debugpy
ENTRYPOINT [ "python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "bot.py" ]