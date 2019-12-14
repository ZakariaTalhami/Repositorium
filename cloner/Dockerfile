FROM python:3

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY ./cloner ./
COPY ./communication ./communication
COPY ./models ./models
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]