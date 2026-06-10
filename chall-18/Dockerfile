FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y steghide --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN pip install flask pillow --no-cache-dir
COPY . .
EXPOSE 5000
CMD sh -c 'python3 generate_images.py && printf "%s" "$FLAG" > /tmp/flag.txt && steghide embed -cf static/images/image_34.jpg -ef /tmp/flag.txt -p "" -f && rm /tmp/flag.txt && python app.py'
