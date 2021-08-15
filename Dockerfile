# set base image (host OS)
FROM python:3.7-slim-buster

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY BirthdayCog.py BirthdayCog.py
COPY BDayBot.py BDayBot.py 

# command to run on container start
CMD [ "python", "./BDayBot.py" ]