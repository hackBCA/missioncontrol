from flask import url_for, render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from . import admin_module as mod_admin
from . import controllers as controller
from .forms import *
from application import CONFIG
from application import cache

@cache.cached()
@mod_admin.route("/admin", methods = ["GET", "POST"])
def foo():
	if request.method == "POST":
		user = request.form["email"]
		return redirect(url_for('.edit_member', user = user))
	stuff = controller.get_users()
	return render_template("admin.index.html", stuff = stuff)


@cache.cached()
@mod_admin.route("/admin/new", methods = ["GET", "POST"])
def add_member():
	form = StaffForm(request.form)

	if request.method == "POST" and form.validate():
		try:
			#controller validation
			controller.add_user(request.form["first_name"], request.form["last_name"], request.form["email"], request.form["password"], request.form["roles"])
			#redirect to main admin page
			return redirect("/admin")
		except Exception as e:
			exceptionType = e.args[0]
			if exceptionType == "UserExistsError":
				flash("A staff member with that email already exists.")
			else:
				if CONFIG["DEBUG"]:
					raise e
				else:
					flash("Something went wrong.", "error")
	return render_template("admin.new.html", form = form)

@cache.cached()
@mod_admin.route("/admin/edit", methods = ["GET", "POST"])
def edit_member():
	form = StaffUpdateForm(request.form)

	if request.method == "POST" and form.validate():
		try:
			#EDIT the staff member
			controller.edit_user(request.form["first_name"], request.form["last_name"], request.form["email"], request.form["roles"])
			return redirect("/admin")
		except Exception as e:
			if CONFIG["DEBUG"]:
				raise e
			else:
				flash("Something went wrong.", "error")
	user = controller.get_user(request.args.get("user"));
	form.first_name.data = user.firstname
	form.last_name.data = user.lastname
	form.email.data = user.email
	form.roles.data = ""
	if len(user.roles) >= 1:
		form.roles.data = user.roles[0]
		for i in range(1, len(user.roles)):
			form.roles.data += ", " + user.roles[i]
	return render_template("admin.edit_user.html", user = user, form = form)

@cache.cached()
@mod_admin.route("/admin/delete", methods = ["GET", "POST"])
def delete_member():
	if request.method == "POST":
		controller.delete_user(request.form["email"])
		flash("User Deleted")
	return redirect("/admin");