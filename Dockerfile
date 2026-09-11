FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/

RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements/base.txt ]; then \
        pip install --no-cache-dir -r requirements/base.txt; \
       elif [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
       fi

COPY . .

RUN mkdir -p media staticfiles vector_store

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]