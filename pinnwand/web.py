#!/usr/bin/env python
import json

from datetime import timedelta
from functools import partial

from flask import Flask
from flask import render_template, url_for, redirect, request, make_response

from pinnwand.models import Paste
from pinnwand.models import session
from pinnwand.helpers import list_languages

app = Flask(__name__)

app.debug = True

@app.teardown_appcontext
def teardown_session(response):
    session.remove()

class ValidationException(ValueError):
    def __init__(self, fields):
        self.fields = fields

def do_paste(raw=None, lexer="text", expiry="1week", src="web"):
    lexers = list_languages()
    errors = []

    if not lexer in lexers:
        errors.append("lexer")

    if not raw:
        errors.append("raw")

    expiries = {"1day": timedelta(days=1),
                "1week": timedelta(days=7),
                "1month": timedelta(days=30),
                "never": None}

    if not expiry in expiries:
        errors.append("expiry")
        return template(message="Please don't make up expiry dates.")
    else:
        expiry = expiries[expiry]

    if errors:
        raise ValidationException(errors)
    else:
        return Paste(raw, lexer=lexer, expiry=expiry, src=src)

@app.route("/", methods=["GET"])
@app.route("/+<lexer>")
def index(lexer=""):
    return render_template("new.html", lexer=lexer,
               lexers=list_languages(), pagetitle="new")

@app.route("/", methods=["POST"])
@app.route("/json", methods=["POST"], defaults={"wants_json": True})
def paste(wants_json=False):
    print request.form

    lexer  = request.form["lexer"]
    raw    = request.form["code"]
    expiry = request.form["expiry"]

    template = partial(render_template, "new.html", lexer=lexer,
            lexers=list_languages(), pagetitle="new")

    try:
        paste = do_paste(raw, lexer, expiry)
    except ValidationException:
        return template(message="It didn't validate!")

    session.add(paste)
    session.commit()

    if wants_json:
        response = make_response(json.dumps({"paste_id": paste.paste_id,
                                            "removal_id": paste.removal_id}))
        response.headers["content-type"] = "application/json"
    else:
        response = redirect(url_for("show", paste_id=paste.paste_id))
        response.set_cookie("removal", str(paste.removal_id), path=url_for("show", paste_id=paste.paste_id))

    return response


@app.route("/show/<paste_id>")
def show(paste_id):
    paste = session.query(Paste).filter(Paste.paste_id == paste_id).first()

    if not paste:
        return render_template("404.html"), 404

    can_delete = request.cookies.get("removal") == str(paste.removal_id)

    return render_template("show.html", paste=paste, pagetitle="show",
            can_delete=can_delete)

@app.route("/raw/<paste_id>")
def raw(paste_id):
    paste = session.query(Paste).filter(Paste.paste_id == paste_id).first()

    if not paste:
        return render_template("404.html"), 404

    response = make_response(paste.raw)
    response.headers["content-type"] = "text/plain"

    return response

@app.route("/remove/<removal_id>")
def remove(removal_id):
    paste = session.query(Paste).filter(Paste.removal_id == removal_id).first()

    if not paste:
        return render_template("404.html"), 404

    session.delete(paste)
    session.commit()

    return redirect(url_for("index"))

@app.route("/removal")
def removal():
    return render_template("removal.html", pagetitle="removal")

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
