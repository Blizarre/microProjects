from flask import Flask, request, send_file
import requests
from openai import OpenAI
import os

if os.path.isfile("key"):
    with open("key") as fd:
        api_key = fd.readline()
else:
    api_key = None

client = OpenAI(api_key=api_key)

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
