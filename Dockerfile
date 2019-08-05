FROM python:latest

# Chromaprint dependencies
RUN wget https://www.deb-multimedia.org/pool/main/d/deb-multimedia-keyring/deb-multimedia-keyring_2016.8.1_all.deb
RUN dpkg -i deb-multimedia-keyring_2016.8.1_all.deb
RUN echo "deb http://www.deb-multimedia.org buster main non-free" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install ffmpeg libchromaprint-tools -y

# Python dependencies
RUN pip install eyed3 ffmpeg-python lyricsgenius musicbrainzngs pyacoustid pymssql watchdog

# App
COPY . /app
WORKDIR "/app"
CMD python __init__.py
