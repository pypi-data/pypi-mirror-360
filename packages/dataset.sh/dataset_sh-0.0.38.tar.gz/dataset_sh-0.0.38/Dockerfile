
FROM node:20 AS frontend-builder

WORKDIR /app/app-ui

COPY app-ui/package.json package.json
COPY app-ui/yarn.lock yarn.lock

RUN yarn install

COPY app-ui/ ./
RUN yarn build   # produces output in /app/frontend/dist
RUN yarn node scripts/package.cjs

FROM python:3 AS final

WORKDIR /app

RUN mkdir -p /app
RUN mkdir -p /app/data
RUN mkdir -p /app/posts
RUN mkdir -p /app/uploader

COPY readme.md readme.md
COPY pyproject.toml pyproject.toml
COPY src src

COPY --from=frontend-builder /app/app-ui/frontend.zip ./src/dataset_sh/server/assets/app-ui.frontend

RUN pip install -e .
RUN pip install gunicorn

ENV DSH_APP_STORAGE_DIR=/app/data
ENV DSH_APP_ARTICLE_DIR=/app/posts
ENV DSH_APP_UPLOADER_DIR=/app/uploader

ENV DATASET_SH_SERVER_CONFIG_FILE=/app/dataset-sh-server-config.json
ENV DSH_APP_HOSTNAME=localhost:8989

RUN dataset.sh server config init

CMD ["gunicorn"  , "-b", "0.0.0.0:8989", "dataset_sh.server.app:create_app()"]
