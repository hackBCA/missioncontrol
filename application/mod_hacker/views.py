from flask import render_template, redirect, request, flash, session, jsonify
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
  participants = controller.get_participants(0, 50)
  participants = controller.summarize_participants(participants)

  return render_template("hacker.search.html", participants = json.dumps(participants))

@mod_hacker.route("/api/get_participants", methods = ["GET"])
def api_get_participants():
  print(request.args)
  if "page_num" not in request.args or "page_size" not in request.args:
    return jsonify(status = -1, message = "Missing request parameters.")

  participants = controller.get_participants(int(request.args["page_num"]), int(request.args["page_size"]))
  participants = controller.summarize_participants(participants)

  return json.dumps(participants)