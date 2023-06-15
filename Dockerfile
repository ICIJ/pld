FROM python:3.8-buster

RUN apt update && apt install -y \
  tesseract-ocr \
  tesseract-ocr-all \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION 1.3.1
ENV POETRY_HOME "/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT true
ENV POETRY_NO_INTERACTION  1
ENV PATH "$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - -y --version $POETRY_VERSION

# Python 3 surrogate unicode handling
# @see https://click.palletsprojects.com/en/7.x/python3/
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /opt/app

COPY . .
RUN poetry install

ENTRYPOINT ["poetry", "run"]
CMD ["pld", "--help"]
