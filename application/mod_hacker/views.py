from flask import render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from . import hacker_module as mod_hacker
from . import controllers as controller
from application import CONFIG
from .forms import RateForm

@mod_hacker.route("/email")
def send_mass_email():
	#controller.send_unconfirmed_email()
	return render_template("hacker.email.html")

@mod_hacker.route("/search")
def search():
	return render_template("hacker.search.html")

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