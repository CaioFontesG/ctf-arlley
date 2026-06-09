FROM python:3.11-slim
WORKDIR /app
RUN pip install flask requests --no-cache-dir
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
