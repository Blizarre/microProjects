# MicroDallE

This project is a web server that creates an image based on a user-input prompt. It is using DallE 3 (require an OpenAI account)

## Files

- `server.py``: Flask server that serves an HTML page and runs an image generating function when a form on the HTML page is submitted.
- `index.html`: HTML page that takes user input and sends it to the Flask server.
- Dockerfile: Dockerfile to build a container for running this project.
- `requirements.txt`: Python dependencies needed for this project.
- `inprogress.gif`: a GIF shown in the user interface while the image is being generated.

## Dependencies
- Flask: Used to host the HTML page and run the image generation on form submission.
- OpenAI: Used to generate images.

## Run Instructions

- First, build the Docker image as follows:
```shell
docker build -t microdalle .
```
- Run the Docker image:
```shell
docker run -e OPENAI_API_KEY=YOUR_KEY -p 8000:8000 microdalle
```
- Open your web browser and visit http://localhost:8000.
- Enter your parameters in the form and click `Generate` to generate an image.