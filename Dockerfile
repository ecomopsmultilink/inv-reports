# Dockerfile
FROM python:3.9-slim


# Copy script and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY script.py .
RUN mkdir -p templates
COPY index.html templates/index.html

CMD ["python", "script.py"]

