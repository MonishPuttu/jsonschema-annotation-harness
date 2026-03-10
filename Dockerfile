FROM python:3.14.0-alpine

WORKDIR /app

RUN pip install --no-cache-dir jsonschema packaging

COPY annotation_runner.py .

CMD ["python", "/app/annotation_runner.py"]
