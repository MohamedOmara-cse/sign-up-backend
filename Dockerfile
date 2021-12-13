# Using lightweight alpine image
FROM python:3.8-alpine

# Installing packages
RUN apk update && apk add build-base bash postgresql-libs && \
    apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev && \
    apk add --no-cache --update libffi-dev
RUN pip install --upgrade pip && pip install --no-cache-dir pipenv gunicorn

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000
CMD [ "gunicorn", "-w", "3", "-b", ":5000", "app" ]