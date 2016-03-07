from flask import render_template, redirect, request, flash, session, jsonify, abort, Response, stream_with_context
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG
import json
from .forms import RateForm, AcceptForm

@mod_hacker.route("/email")
def send_mass_email():
    #controller.send_unconfirmed_email()
    return render_template("hacker.email.html")

@mod_hacker.route("/search")
def search():
    return render_template("hacker.search.html")

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

@mod_hacker.route("/applicant/<uid>")
def applicant_view(uid):
    applicant = controller.get_applicant_dict(uid)
    if applicant is None:
        abort(404)
    return render_template("hacker.applicant.html", applicant = applicant)

@mod_hacker.route("/review", methods = ["GET", "POST"])
def review():
    form = RateForm(request.form)

    if request.method == "POST" and form.validate():
        if "active_app" in session:
            controller.review_application(session["active_app"], int(form["rating"].data), current_user.email)
            flash("User successfully reviewed.", "success")
            session.pop("active_app")       
        else:
            flash("Something went wrong.", "error")

    if "active_app" in session:
        active_app_email = session["active_app"]
        user = controller.get_participant(active_app_email)
    else:
        user = controller.get_next_application(current_user.email)
        if user is not None:
            session["active_app"] = user.email
        
    return render_template("hacker.review.html", form = form, user = user)

@mod_hacker.route("/accept", methods = ["GET", "POST"])
def accept():
    form = AcceptForm(request.form)

    if request.method == "POST":
        if form.validate():
            try:
                action = request.form['action']
                if action == "accept":
                    info = controller.accept_applicants(form["type_account"].data, int(form["block_size"].data))    
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
