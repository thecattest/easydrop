from flask import Flask, request, make_response, jsonify, Response, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from db_init import *
import os
from tg import updater, bot, NetworkError, CHAT_ID


app = Flask(__name__)
app.config['SECRET_KEY'] = 'easydropsecretkthatyouwillneverguessbutcaneasilyfindongithub'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.unauthorized_handler(callback=(lambda: redirect('/login')))


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    db.expire_on_commit = False
    return db.query(User).get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login_handler():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form_data = request.form
        form_login = form_data["login"].strip()
        form_password = form_data["password"].strip()
        db = db_session.create_session()
        form_user = db.query(User).filter(User.login == form_login).first()
        db.close()
        if form_user:
            if form_user.check_password(form_password):
                login_user(form_user, True)
                return redirect("/")
            else:
                return render_template("login.html",
                                       alert_text="wrong password",
                                       login=form_login)
        else:
            return render_template("login.html",
                                   alert_text="login does not exist")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout_handler():
    logout_user()
    return redirect("/login")


@app.route("/")
@login_required
def index():
    # return send_html("index.html")
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        try:
            bot.send_document(current_user.id, file, filename=file.filename)
        except NetworkError as e:
            bot.send_message(CHAT_ID, str(e))
            path = 'files/' + file.filename
            if not os.path.exists("files"):
                os.mkdir("files")
            with open(path, 'wb') as temp:
                temp.write(file.read())
    return make_response(jsonify({"answer": "ok"}), 200)


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


if __name__ == '__main__':
    main()
