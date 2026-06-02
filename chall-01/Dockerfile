FROM python:3.11-slim
WORKDIR /app
RUN pip install flask --no-cache-dir
COPY . .
EXPOSE 9099
CMD ["python", "app.py"]
