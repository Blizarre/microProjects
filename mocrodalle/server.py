import os

from flask import Flask, request, send_file
from openai import OpenAI


def api_key():
    if os.path.isfile("key"):
        with open("key", encoding="utf=8") as fd:
            return fd.readline().strip()
    return None


client = OpenAI(api_key=api_key())

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    # Get the text from the user
    prompt = request.json["prompt"]
    hd = request.json["hd"]
    size = request.json["size"]

    print("Making request with", prompt)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=hd,
        n=1,
    )
    url = response.data[0].url
    print("Response received", url)

    return url


@app.route("/", methods=["GET"])
def index():
    return send_file("index.html", mimetype="text/html")


@app.route("/inprogress.gif", methods=["GET"])
def inprogress():
    return send_file("inprogress.gif", mimetype="image/gif")


if __name__ == "__main__":
    app.run(debug=True)
