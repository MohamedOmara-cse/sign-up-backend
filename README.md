# StormIQ API

## Dev

Run the application:

```
python app.py
```

## Setup

Create the virtual environment. ‘venv' can be replaced with any appropriate name.

```
python3 -m venv venv/
```

Enter the virtual environment

```
source venv/bin/activate
```

List & install dependencies

```
pip list
pip install numpy
```

Freeze dependencies

```
pip freeze > requirements.txt
```

Install saved dependencies

```
pip install -r requirements.txt
```

Exit the environment

```
deactivate
```

Destroy the environment

```
rm -r venv/
```

## Deployment

### Manual deployment

Zip the repo:

```
git archive -v -o api-deployment.zip --format=zip HEAD
```

Upload and deploy via Elastic Beanstalk console in AWS.
