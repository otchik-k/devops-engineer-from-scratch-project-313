FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app

#RUN pip3 install --no-cache-dir uv
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

RUN apk update && apk add nginx
RUN apk add --no-cache bash
#RUN apk add --no-cache gunicorn

#COPY ./application /app
COPY . /app
COPY ./services/project-devops-deploy-crud-frontend/dist/. /app/publ
COPY ./services/nginx.conf /etc/nginx

RUN uv sync

RUN cat > /start.sh << 'EOF'
#!/usr/bin/env bash
set -e

nginx

exec gunicorn --bind 0.0.0.0:5000 application.main:app
EOF
RUN chmod +x /start.sh

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
