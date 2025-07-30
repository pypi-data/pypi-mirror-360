FROM python:3 AS final

WORKDIR /app

RUN mkdir -p /app
RUN mkdir -p /app/data
RUN mkdir -p /app/posts
RUN mkdir -p /app/uploader

COPY readme.md readme.md
COPY pyproject.toml pyproject.toml
COPY src src
COPY tests tests

RUN pip install -e .
RUN pip install pytest pandas tqdm

CMD ["pytest","tests"]
