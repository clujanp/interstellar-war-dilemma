FROM python:3.11-slim

WORKDIR /app

COPY config/requirements/development.txt config/requirements/development.txt
COPY app/ .

RUN pip install --no-cache-dir -r config/requirements/development.txt

EXPOSE 5000

COPY config/docker/start-app.sh /start-app.sh
RUN chmod +x /start-app.sh

ENTRYPOINT ["/start-app.sh"]
