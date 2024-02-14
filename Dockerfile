# python3.11のイメージをダウンロード
FROM python:3.11-slim-buster
# pythonの出力表示をDocker用に調整
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# pipを使ってpoetryをインストール
RUN pip install --no-cache-dir poetry==1.4.2

# poetryの定義ファイルをコピー (存在する場合)
COPY pyproject.toml* poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.create false && \
    if [ -f pyproject.toml ]; then poetry install --no-root --no-interaction --no-ansi; fi

# uvicornのサーバーを立ち上げる
ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload"]