# Base on https://github.com/orgs/python-poetry/discussions/1879#discussioncomment-7284113

# python3.11のイメージをダウンロード
FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y curl

ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.4.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # never create virtual environment automaticly, only use env prepared by us
    POETRY_VIRTUALENVS_CREATE=false \
    \
    # this is where our requirements + virtual environment will live
    VIRTUAL_ENV="/venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

# create python virtual environment
RUN python -m venv $VIRTUAL_ENV

WORKDIR /src

ENV PYTHONPATH="/src:$PYTHONPATH"

# poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3 -

# poetryの定義ファイルをコピー
COPY pyproject.toml poetry.lock ./

# poetryでライブラリをインストール
RUN poetry install --no-root

EXPOSE 8000

# uvicornのサーバーを立ち上げる
ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
