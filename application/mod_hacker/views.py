from flask import render_template, redirect, request, flash, session, jsonify, abort, Response, stream_with_context
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from .forms import RateForm, AcceptForm, SmsBlastForm
from application import CONFIG
from application.mod_admin.permissions import sentinel
import json, os, time

@mod_hacker.route("/email")
@login_required
@sentinel.board.require(http_exception = 403)
def send_mass_email():
    #controller.send_unconfirmed_email()
    #controller.send_not_started_email()
    #controller.send_in_progress_email()
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
    user = controller.get_applicant_by_id(uid)
    if 'check-in' in request.form:
      if 'checked_in' in user and user['checked_in']:
        flash("User is already checked in.", "error")
      else:
        controller.check_in_status_user(user, True)
    elif 'check-out' in request.form:
      if 'checked_in' in user and not user['checked_in']:
        flash("User is already checked out.", "error")
      else:
        controller.check_in_status_user(user, False)
    elif 'manual-accept' in request.form:
      if sentinel.board.can():
        controller.accept_applicant(user)
        flash("User manually accepted.", "success")
      else:
        flash("Sorry, you don't have permission to do this.", "error")
  applicant = controller.get_applicant_dict(uid)  

  if applicant is None:
      abort(404)

  if "check_in_log" in applicant.keys():
    check_in_log = [list(row) for row in applicant["check_in_log"]] #Have to do this for some reason
    for k in range(len(check_in_log)):
      check_in_log[k][1] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(check_in_log[k][1]))
    applicant["check_in_log"] = check_in_log

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

@mod_hacker.route("/smsblast", methods = ["GET", "POST"])
@login_required
@sentinel.sms_blast.require()
def smsblast():
  form = SmsBlastForm(request.form)
  print(controller.get_staff_phone_nums())
  if request.method == "POST" and form.validate():
    try:
      sent_stats = controller.sms_blast(form['type_accounts'].data, form['message'].data)
      flash("%d messages sent. %d failed." % sent_stats, "neutral")
    except Exception as e:
      if CONFIG["DEBUG"]:
        raise e
      flash("Something went wrong.", "error")
      
  return render_template("hacker.sms_blast.html", form = form)

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

@mod_hacker.route("/api/accept_applicant", methods = ["POST"])
def api_accept_user():
  if request.json["secret-key"] != CONFIG["SECRET_KEY"]:
    return json.dumps({"success" : "0", "error" : "Invalid secret key."})
  try:
    user = controller.get_applicant_by_id(request.json["user-id"])
    if user['decision'] == 'Accepted':
      return json.dumps({"success": "0", "error": "User already accepted."})
    controller.accept_applicant(user)
    return json.dumps({"success" : "1"})
  except Exception as e:
    return json.dumps({"success" : "0", "error" : "Something went wrong."})