FROM  python:3.14-alpine AS builder

WORKDIR /app

#COPY requirements.txt /app

RUN pip3 install --no-cache-dir uv
#RUN --mount=type=cache,target=/root/.cache/pip \
#    pip3 install -r requirements.txt

RUN apk update && apk add nginx
RUN apk add --no-cache bash
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/*n
RUN apk add --no-cache \
    build-base \
    postgresql-dev

COPY ./application/. /app
COPY . /app
COPY ./services/project-devops-deploy-crud-frontend/dist/. /app/publ
COPY ./services/nginx.conf /etc/nginx
COPY ./start.sh /

RUN uv sync

#RUN cat > /start.sh << 'EOF'
#!/usr/bin/env bash
#set -e

#nginx

#cd /app/application

#exec uv run gunicorn --bind 0.0.0.0:8080 main:app
#EOF
#RUN chmod +x /start.sh

# Открываем порт, который слушает Nginx (80)
EXPOSE 80

# Точка входа: запускаем оба сервиса
CMD ["/start.sh"]

#ENTRYPOINT ["uv", "run"]
#CMD ["python3", "application/main.py"]

#FROM builder AS dev-envs

#RUN apk update && apk add --no-cache git docker-cli

#RUN addgroup -S docker && \
#    adduser -S vscode -G docker -s /bin/bash && \
#    chown -R vscode:docker /app

#USER vscode
