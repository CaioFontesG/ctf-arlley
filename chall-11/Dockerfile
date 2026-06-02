FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y iputils-ping --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN pip install flask pyjwt --no-cache-dir
COPY . .
EXPOSE 5000
CMD sh -c 'echo "$FLAG" > /flag.txt && python app.py'
