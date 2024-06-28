FROM python:3.10-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache bash
    
RUN apk add build-base
RUN apk add libffi-dev
COPY ./src/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./src/ ./
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 80/tcp
CMD ["./docker-entrypoint.sh"]
