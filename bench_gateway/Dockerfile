FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
      --trusted-host pypi.org \
      --trusted-host files.pythonhosted.org \
      --trusted-host pypi.python.org \
      -r requirements.txt

COPY mock_auth.py mock_downstream.py gateway.py ./
