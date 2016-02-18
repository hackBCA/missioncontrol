from flask import render_template, redirect, request, flash, session, abort
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG

@mod_hacker.route("/email")
def send_mass_email():
  controller.send_in_progress_email()
  return render_template("hacker.email.html")

@mod_hacker.route("/applicant/<uid>")
def applicant_view(uid):
  applicant = controller.get_applicant_by_id(uid)
  if applicant is None:
    abort(404)
  return render_template("hacker.applicant.html", applicant = applicant)
