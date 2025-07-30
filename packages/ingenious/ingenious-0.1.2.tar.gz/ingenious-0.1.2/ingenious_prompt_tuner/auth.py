from functools import wraps

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# Authentication Helpers

bp = Blueprint("auth", __name__, url_prefix="/auth")


# Routes
@bp.route("/login", methods=["GET", "POST"])
def login():
    def check_auth(username, password):
        return (
            username == current_app.config["username"]
            and password == current_app.config["password"]
        )

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if check_auth(username, password):
            session["logged_in"] = True
            return redirect(url_for("index.home"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated
