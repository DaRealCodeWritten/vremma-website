import flask
import flask_login
import mariadb
import os
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_login import login_required, current_user
from passlib.context import CryptContext
from flask import Blueprint, flash, request, redirect, abort, render_template, url_for, current_app


login_blueprint = Blueprint("login", __name__)
context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

class AnonymousUser(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.user_id = -1
        self.username = None
        self.registered = 0
        self.permissions = -1
        super().__init__()

    def is_authenticated(self):
        return False

    def get_id(self):
        return self.user_id


class User(flask_login.UserMixin):
    def __init__(self, user_id: int, username: str, email: str, registered: datetime, permissions: int):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.registered = registered
        self.permissions = permissions
        super().__init__()

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.user_id


class LoginForm(FlaskForm):
    username = StringField("username", validators=(DataRequired(),), id="email")
    password = PasswordField("password", validators=(DataRequired(),), id="password")
    submit = SubmitField("Log In", id="loginbutton")


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "GET":
        if len(request.args) > 0:
            if request.cookies.get("NO_ERROR_ON_RELOAD"):
                resp = flask.make_response(flask.redirect("/login"))
                resp.delete_cookie("NO_ERROR_ON_RELOAD")
                return resp
            error = request.args.get("error")
            if error == "1":
                resp = flask.make_response(render_template("login/login.html", error=True, form=form))
                resp.set_cookie(
                    "NO_ERROR_ON_RELOAD", "1"
                )
                return resp
        return render_template("login/login.html", form=form)
    elif form.validate_on_submit():
        uname = form.username.data
        password = form.password.data
        if not (uname and password):
            return redirect(url_for("login.login", error="1"))
        db = mariadb.connect(
            host="localhost",
            database="vremma_website",
            user=os.getenv("DATABASE_USER"),
            passwd=os.getenv("DATABASE_PASS")
        )
        crs = db.cursor()
        crs.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s", (uname, uname)
        )
        result = crs.fetchall()
        crs.close()
        db.close()
        if len(result) == 0:
            return redirect(url_for("login.login", error="1"))
        elif len(result) > 1:
            return abort(500)
        if context.verify(password, result[0][2].encode("UTF-8")):
            user = User(
                    result[0][5],
                    result[0][0],
                    result[0][1],
                    result[0][4],
                    result[0][3]
                )
            flask_login.login_user(user)
            current_app.config["USERS"][result[0][5]] = user
            return redirect("/")
        else:
            return redirect(url_for("login.login", error="1"))

@login_blueprint.route("/logout")
@login_required
def logout():
    current_app.config["USERS"].pop(current_user.get_id())
    flask_login.logout_user()
    return redirect("/")
