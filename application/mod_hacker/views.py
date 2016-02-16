from flask import render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG

@mod_hacker.route("/email")
def send_mass_email():
  controller.send_unconfirmed_email()
  return render_template("hacker.email.html")

@mod_hacker.route("/search")
def search():
  return render_template("hacker.search.html")