import flask_login
import flask
import dotenv
import os
import flask_wtf
from flask import request

from blueprints import login as bp_login
from blueprints import projects as bp_projects

dotenv.load_dotenv()
app = flask.Flask(__name__)
app.secret_key = os.getenv("WEBSITE_SECRET")
login = flask_login.LoginManager()
login.init_app(app)
flask_wtf.CSRFProtect(app)
app.config["USERS"] = {}


@login.user_loader
def load_user(user_id):
    return app.config["USERS"].get(user_id)


@app.route("/")
def index():
    return flask.render_template("base.html")


@app.route("/favicon.ico")
def favicon():
    return flask.redirect(flask.url_for('static', filename='favicon.ico'))

@app.errorhandler(Exception)
def on_error(_):
    return flask.redirect(flask.url_for("error", error_code=500))

@app.route("/error")
def error():
    error_code = request.args.get("error_code")
    if not error_code:
        return flask.render_template("error.html", error_code=500, error_message="An unknown error occurred and the last webpage failed to redirect properly")
    else:
        return flask.render_template("error.html", error_code=error_code, error_message="Something went quite wrong. This will be investigated!")


app.register_blueprint(bp_login.login_blueprint)
app.register_blueprint(bp_projects.project)

app.run(debug=True)
