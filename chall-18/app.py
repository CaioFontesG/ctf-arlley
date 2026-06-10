import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

IMAGES = [f"image_{i:02d}.jpg" for i in range(1, 51)]

@app.route("/")
def index():
    return render_template("index.html", images=IMAGES)

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory("static/images", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
