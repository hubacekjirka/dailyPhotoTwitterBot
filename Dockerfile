FROM python:3.7-alpine

# RUN apk --update add gcc libgcc musl-dev
# RUN apk add jpeg-dev zlib-dev

RUN apk --update add gcc libgcc musl-dev jpeg-dev zlib-dev


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["/bin/sh"]