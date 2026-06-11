from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory("static/images", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
