FROM python:3.12.3-slim

COPY . .

RUN apt update -y && apt install curl -y

RUN pip install -r requirements.txt 

ENTRYPOINT ["pytest"]
