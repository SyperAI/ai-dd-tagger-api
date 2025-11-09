import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, abort
from gradio_client import Client, handle_file


JUNK_TAGS = ['rating:explicit', 'rating:safe', 'rating:questionable']
ALLOWED_ORIGINS = {"https://rule34.gg", "127.0.0.1", "http://127.0.0.1:8080"}

app = Flask(__name__)
client = Client("hysts/DeepDanbooru")

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

@app.route('/')
def hello_world():  # put application's code here
    return jsonify({
        'msg': "This API is used to determine the tags of the picture, as well as its rating"
    })


@app.put("/predict")
def predict():
    file_path = None

    # Obtaining a file and checking for the correctness of its transmission
    if request.args.get('image_url', None) is None:
        file = request.files['file']
        if not file:
            return jsonify({'msg': "You need to add file!"}), 400
        if not hasattr(file, 'name') or not file.name:
            file.name = file.filename
        file.seek(0)

        # Maintenance of the file in the temporary storage folder
        save_path = Path(tempfile.gettempdir(), "rule34", "ai_tagger")
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = Path(save_path, os.path.basename(file.filename))
        file.save(file_path)
    else:
        file_path = request.args.get('image_url')

    # Request to Hugging Face to receive data about the picture
    result = client.predict(
        image=handle_file(file_path),
        score_threshold=0.5,
        api_name="/predict"
    )

    if request.args.get('image_url', None) is None:
        # Removing temporary file
        os.remove(file_path)

    # Parsing picture info
    tags: list = result[-1].split(", ")

    rating = 'questionable'
    if 'rating:explicit' in tags:
        rating = 'explicit'
    elif 'rating:safe' in tags:
        rating = 'safe'

    return jsonify({
        'rating': rating,
        'tags': [tag for tag in tags if tag not in JUNK_TAGS],
    })


@app.before_request
def before_request():
    try:
        request.remote_addr = request.environ['HTTP_X_FORWARDED_FOR'].split(", ")[0]
    except KeyError:
        pass

    origin = request.headers.get('Origin', default=request.remote_addr)
    if origin not in ALLOWED_ORIGINS and request.remote_addr not in ALLOWED_ORIGINS:
        abort(403, description='Origin not allowed')


@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', default=request.remote_addr)
    if request.headers.get('Origin') in ALLOWED_ORIGINS or request.remote_addr in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = \
            'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = \
            'GET, PUT, OPTIONS'

    return response


if __name__ == '__main__':
    app.run()
