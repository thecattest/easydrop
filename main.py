from flask import Flask, request, make_response, jsonify, Response
import os
import telegram

try:
    from tg import TOKEN, CHAT_ID
except ImportError:
    print('Telegram config file not found')
    TOKEN = ''
    CHAT_ID = ''


app = Flask(__name__)
bot = telegram.Bot(TOKEN)


def main():
    port = int(os.environ.get("PORT", 5003))
    host = "0.0.0.0"
    from waitress import serve
    serve(app, host=host, port=port)
    # app.run(host=host, port=port)


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        return open(src)
    except IOError as exc:
        return str(exc)


def send_html(name):
    content = get_file(os.path.join("templates", name)).read()
    return Response(content, mimetype="text/html")


@app.route("/")
def index():
    return send_html("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        try:
            bot.send_document(CHAT_ID, file, filename=file.filename)
        except telegram.error.NetworkError as e:
            bot.send_message(CHAT_ID, str(e))
            path = 'files/' + file.filename
            if not os.path.exists("files"):
                os.mkdir("files")
            with open(path, 'wb') as temp:
                temp.write(file.read())
    return make_response(jsonify({"answer": "ok"}), 200)


if __name__ == '__main__':
    main()
