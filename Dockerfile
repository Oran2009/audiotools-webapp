FROM python:3.8.2

EXPOSE 80 2222

WORKDIR /user/src/app

COPY 'requirements.txt' .

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev && \
    apt-get install -y libsndfile1 && \
    apt-get install -y ffmpeg

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "app.py"]