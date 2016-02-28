from flask import render_template, redirect, request, flash, session, jsonify, abort, Response, stream_with_context
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG
import json

@mod_hacker.route("/email")
def send_mass_email():
  #controller.send_unconfirmed_email()
  return render_template("hacker.email.html")

@mod_hacker.route("/search")
def search():
  accounts = controller.get_all_accounts()
  summarized = controller.summarize_participants(accounts)

  return render_template("hacker.search.html")

@mod_hacker.route("/api/get_participants", methods = ["GET"])
def api_get_participants():
  accounts = controller.get_all_accounts()
  summarized = controller.summarize_participants(accounts)
  return Response(
    stream_with_context(controller.sse_load(summarized)),
    mimetype = "text/event-stream"
  )

  return json.dumps(participants)

@mod_hacker.route("/applicant/<uid>")
def applicant_view(uid):
  applicant = controller.get_applicant_dict(uid)
  if applicant is None:
    abort(404)
  return render_template("hacker.applicant.html", applicant = applicant)