FROM python:3.10-alpine

RUN apk update && apk add libmediainfo-dev

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]