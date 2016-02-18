from flask import render_template, redirect, request, flash, session, abort
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG
import json

@mod_hacker.route("/email")
def send_mass_email():
  controller.send_unconfirmed_email()
  return render_template("hacker.email.html")

@mod_hacker.route("/search")
def search():
  participants = controller.get_participants(0, 1000)
  participants = [{
    'id':           str(person.id),
    'firstname':    person.firstname,
    'lastname':     person.lastname,
    'email':        person.email,
    'type_account': person.type_account,
    'status':       person.status,
    'school':       person.school if person.school is not None else ''
      }
    for person in participants
  ]
  return render_template("hacker.search.html", participants = json.dumps(participants))

@mod_hacker.route("/applicant/<uid>")
def applicant_view(uid):
  applicant = controller.get_applicant_by_id(uid)
  if applicant is None:
    abort(404)
  return render_template("hacker.applicant.html", applicant = applicant)