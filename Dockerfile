FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app

#RUN pip3 install --no-cache-dir uv
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

RUN uv sync

ENTRYPOINT ["uv", "run"]
CMD ["python3", "application/main.py"]

FROM builder AS dev-envs

#RUN apk update && apk add --no-cache git docker-cli

#RUN addgroup -S docker && \
#    adduser -S vscode -G docker -s /bin/bash && \
#    chown -R vscode:docker /app

#USER vscode
