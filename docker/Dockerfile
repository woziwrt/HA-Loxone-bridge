FROM python:3.12-slim

WORKDIR /app

# Use offline virtualenv with all required deps
COPY docker/venv.tar.gz /opt/venv.tar.gz

RUN mkdir -p /opt/venv \
    && tar -xzf /opt/venv.tar.gz -C /opt/venv --strip-components=1

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Tiny wrapper that expects /app/main.py to be mounted
COPY docker/main-wrapper.py /app/main-wrapper.py

CMD ["python", "/app/main-wrapper.py"]
