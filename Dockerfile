
##########################################
# Local Config                           #
##########################################

FROM python:3.10
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8080

# The ENTRYPOINT line is not necessary, CMD is sufficient for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

##########################################
# GCP CONFIG                             #
##########################################

# # Use an official Python runtime as a parent image
# FROM python:3.10

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# ENV PORT=8080

# # Set work directory
# WORKDIR /app

# # Install dependencies
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project
# COPY . /app/

# # Collect static files
# RUN python manage.py collectstatic --noinput

# # Make port available to the world outside this container
# EXPOSE $PORT

# # Run the application:
# #CMD gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
# # CMD gunicorn gptclone.wsgi:application --bind 0.0.0.0:$PORT

# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "your_project_name.wsgi:application"]


##########################################
# Below are Reminder Commands            #
##########################################

# docker build -t susie_django:latest --no-cache .
# docker run -p 8080:8080 susie_django:latest
# or
# docker run --name susie_django_run -p 8080:8080 susie_django:latest

# gcloud
# gcloud auth list
# gcloud config set account `ACCOUNT` # select account
# gcloud projects list # show project list
# gcloud config set project `PROJECT ID` or 'gcloud config set project cpras-toolbox'      # select project ID 
# 
# gcloud builds submit --tag gcr.io/<PROJECT_ID>/<SOME_PROJECT_NAME> --timeout=2h or gcloud builds submit --tag gcr.io/cpras-toolbox/susie_django_poc_v1 --timeout=2h