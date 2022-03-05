FROM python:3.10-alpine

ENV TZ=Asia/Taipei

RUN apk update && apk add libmediainfo-dev

WORKDIR /

COPY . /

RUN pip install -r requirements.txt

CMD ["python", "app.py"]