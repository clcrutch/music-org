FROM python:3.6
COPY . /app
WORKDIR "/app"

# Chromaprint dependencies
RUN wget https://www.deb-multimedia.org/pool/main/d/deb-multimedia-keyring/deb-multimedia-keyring_2016.8.1_all.deb
RUN dpkg -i deb-multimedia-keyring_2016.8.1_all.deb
RUN echo "deb http://www.deb-multimedia.org buster main non-free" >> /etc/apt/sources.list

# SQL Dependencies
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | tee /etc/apt/sources.list.d/msprod.list

# Install
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install ffmpeg libchromaprint-tools mssql-tools unixodbc-dev -y

# Python dependencies
RUN pip install pipenv
RUN pipenv --python /usr/local/bin/python install

# App
CMD pipenv --python /usr/local/bin/python run /app/__main__.py
