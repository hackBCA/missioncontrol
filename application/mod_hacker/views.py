from flask import render_template, redirect, request, flash, session, jsonify, abort, Response, stream_with_context
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from .forms import RateForm, AcceptForm
from application import CONFIG
from application.mod_admin.permissions import sentinel
import json, os

@mod_hacker.route("/email")
@login_required
@sentinel.admin.require(http_exception = 403)
def send_mass_email():
    #controller.send_unconfirmed_email()
    #controller.send_not_started_email()
    #controller.send_in_progress_email()
    #controller.send_not_rsvped_email()
    return render_template("hacker.email.html")

@mod_hacker.route("/search")
@login_required
@sentinel.read_data.require(http_exception = 403)
def search():
    return render_template("hacker.search.html")

@mod_hacker.route("/applicant/<uid>", methods = ["GET", "POST"])
@login_required
@sentinel.read_data.require()
def applicant_view(uid):
    if request.method == "POST":
      for k in request.form:
        print(k)
      if 'manual-accept' in request.form:
        if sentinel.board.can():
          user = controller.get_applicant_by_id(uid)
          controller.accept_applicant(user)
          flash("User manually accepted.", "success")
        else:
          flash("Sorry, you don't have permission to do this.", "error")
    applicant = controller.get_applicant_dict(uid)
    if applicant is None:
        abort(404)
    return render_template("hacker.applicant.html", applicant = applicant)

@mod_hacker.route("/review", methods = ["GET", "POST"])
@login_required
@sentinel.review_apps.require()
def review():
    form = RateForm(request.form)

    if request.method == "POST" and form.validate():
        if "active_app" in session:
            controller.review_application(session["active_app"], int(form["rating"].data), current_user.email)
            flash("User successfully reviewed.", "success")
            session.pop("active_app")       
        else:
            flash("Something went wrong.", "error")

    user = None
    if "active_app" in session:
        active_app_email = session["active_app"]
        user = controller.get_participant(active_app_email)
        if 'review3' in user:
          user = None
    if user is None:
        user = controller.get_next_application(current_user.email)
        if user is not None:
            session["active_app"] = user.email
        
    return render_template("hacker.review.html", form = form, user = user)

@mod_hacker.route("/accept", methods = ["GET", "POST"])
@login_required
@sentinel.director.require()
def accept():
    form = AcceptForm(request.form)

    if request.method == "POST":
        if form.validate():
            try:
                action = request.form['action']
                info = None
                if action == "accept":
                    info = controller.accept_applicants(form["type_account"].data, int(form["block_size"].data)) 
                elif action == "expire":
                    info = controller.expire_applicants(form["type_account"].data, int(form["block_size"].data))    
                elif action == "waitlist":
                    info = controller.waitlist_applicants(form["type_account"].data, int(form["block_size"].data))
                else:
                    flash("Invalid operation.", "error")
            except Exception as e:
                if CONFIG["DEBUG"]:
                    raise e
                flash("Something went wrong.", "error")             
            if info:
                flash(info, "neutral")
        else:
            flash("Please correct any errors.", "error")

    stats = controller.get_accepted_stats()

    return render_template("hacker.accept.html", form = form, stats = stats)

@mod_hacker.route("/waivers", methods = ["GET", "POST"])
@login_required
@sentinel.board.require()
def waivers():
  if request.method == "POST":
    file = request.files['waiver_doc']
    if file and controller.allowed_file(file.filename, ["csv"]):
      filename = secure_filename(file.filename)
      try: 
        file.save(os.path.join(CONFIG["UPLOAD_FOLDER"], filename))
        users_updated = controller.process_waiver_file(filename)
        flash("CSV Processed. %d users updated." % users_updated, "success")
      except Exception as e:
        if CONFIG["DEBUG"]:
          raise e
        if e[0] == "CsvException":
          flash("Invalid CSV.", "error")
        else:
          flash("Something went wrong.", "error")
    else:
      flash("Invalid CSV.", "error")

  return render_template("hacker.waiver.html")

@mod_hacker.route("/api/get_participants_sse", methods = ["GET"])
def api_get_participants_sse():
  return Response(
    stream_with_context(controller.sse_load_participants()),
    mimetype = "text/event-stream"
  )

@mod_hacker.route("/api/get_participants_ajax", methods = ["GET"])
def api_get_participants_ajax():
    participants = controller.ajax_load_participants()
    return json.dumps(participants)
