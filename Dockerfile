# pull official base image
FROM python:3.9.5-slim-buster

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt .
RUN pip3 install --upgrade pip wheel \
    && pip3 install -r requirements.txt

# copy project
COPY . .

USER root
EXPOSE 8080
CMD ["/bin/bash", "-c", "python3 main.py"]
