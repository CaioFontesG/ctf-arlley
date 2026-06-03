FROM python:3.11-slim
WORKDIR /app
RUN pip install flask --no-cache-dir
RUN mkdir -p /var/secrets /app/docs
COPY docs/ /app/docs/
COPY . .
EXPOSE 5000
CMD sh -c 'echo "$FLAG" > /var/secrets/flag.txt && python app.py'
