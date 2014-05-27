#!/usr/bin/env python
from datetime import timedelta

from flask import Flask
from flask import render_template, url_for, redirect, request

from pinnwand.models import Paste
from pinnwand.models import session
from pinnwand.helpers import list_languages

app = Flask(__name__)

app.debug = True

@app.route("/", methods=["GET"])
@app.route("/+<lexer>")
def index(lexer=""):
    return render_template("new.html", lexer=lexer,
               lexers=list_languages(), pagetitle="new")

@app.route("/", methods=["POST"])
def paste():
    lexer  = request.form["lexer"]
    raw    = request.form["code"]
    expiry = request.form["expiry"]

    if not lexer:
        lexer = "text"

    if not lexer in [pair[0] for pair in list_languages()]:
        return render_template("new.html", lexer=lexer,
                   lexers=list_languages(), pagetitle="new",
                   message="Please don't make up lexers.")

    if not raw:
        return render_template("new.html", lexer=lexer,
                   lexers=list_languages(), pagetitle="new",
                   message="Please don't paste empty pastes.")

    expiries = {"1day": timedelta(days=1),
                "1week": timedelta(days=7),
                "1month": timedelta(days=30),
                "never": None}

    if not expiry in expiries:
        return render_template("new.html", lexer=lexer,
                   lexers=list_languages(), pagetitle="new",
                   message="Please don't make up expiry dates.")
    else:
        expiry = expiries[expiry]

    paste = Paste(raw, lexer=lexer, expiry=expiry)

    session.add(paste)
    session.commit()

    response = redirect(url_for("show", paste_id=paste.paste_id))
    response.set_cookie("removal", str(paste.removal_id), path=url_for("show", paste_id=paste.paste_id))

    return response

@app.route("/show/<paste_id>")
def show(paste_id):
    paste = session.query(Paste).filter(Paste.paste_id == paste_id).first()

    if not paste:
        return render_template("404.html"), 404

    can_delete = False

    print request.cookies.get("removal"), paste.removal_id

    if request.cookies.get("removal") == str(paste.removal_id):
        can_delete = True

    return render_template("show.html", paste=paste, pagetitle="show",
            can_delete=can_delete)

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
    app.run();
