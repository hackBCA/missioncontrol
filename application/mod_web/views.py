from flask import render_template, redirect, request, flash
from flask.ext.login import login_required, current_user
from . import web_module as mod_web
from . import controllers as controller
from application import CONFIG

@mod_web.route("/")
def foo():
  return render_template("web.index.html")