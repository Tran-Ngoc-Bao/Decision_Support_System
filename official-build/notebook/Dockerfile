FROM jupyter/base-notebook:latest

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID:-1000}:${NB_GID:-100}

RUN pip install --no-cache-dir \
    psycopg2-binary \
    sqlalchemy \
    ipython-sql \
    pandas \
    matplotlib \
    seaborn