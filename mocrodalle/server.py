from flask import Flask, request, send_file
import requests
from openai import OpenAI

with open("key") as fd:
    key = fd.readline()

client = OpenAI(api_key=key)

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    # Get the text from the user
    text = request.json.get("text", "")
    print("Making request with", text)

    response = client.images.generate(
        model="dall-e-3",
        prompt=text,
        size="1024x1024",
        quality="standard",
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
