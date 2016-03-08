from flask import url_for, render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from flask.ext.principal import PermissionDenied
from . import admin_module as mod_admin
from . import controllers as controller
from .permissions import sentinel
from .forms import *
from application import CONFIG
from application import cache

@cache.cached()
@mod_admin.route("/admin", methods = ["GET", "POST"])
@login_required
@sentinel.admin.require(http_exception = 403)
def admin():
    if request.method == "POST":
        user = request.form["email"]
        return redirect(url_for('.edit_member', user = user))
    users = controller.get_users()
    return render_template("admin.index.html", users = users)

@cache.cached()
@mod_admin.route("/admin/new", methods = ["GET", "POST"])
@login_required
@sentinel.admin.require(http_exception = 403)
def add_member():
    form = StaffForm(request.form)

    if request.method == "POST" and form.validate():
        try:
            #controller validation
            controller.add_user(request.form["email"].lower(), request.form["first_name"], request.form["last_name"], request.form["password"], request.form.getlist("roles"))
            #redirect to main admin page
            flash("User Added", "success")
            return redirect("/admin")
        except Exception as e:
            exceptionType = e.args[0]
            if exceptionType == "UserExistsError":
                flash("A staff member with that email already exists.", "error")
            else:
                if CONFIG["DEBUG"]:
                    raise e
                else:
                    flash("Something went wrong.", "error")
    return render_template("admin.new.html", form = form)


@cache.cached()
@mod_admin.route("/admin/edit/<uid>", methods = ["GET", "POST"])
@login_required
@sentinel.admin.require(http_exception = 403)
def edit_member(uid):
    form = StaffUpdateForm(request.form)
    print(request.form.getlist("roles"))

    if request.method == "POST" and form.validate():
        try:
            #Edit the staff member
            if "save" in request.form:
                controller.edit_user(request.form["first_name"], request.form["last_name"], request.form["email"], request.form.getlist("roles"))
            elif "cancel" in request.form:
                return redirect("/admin")
            flash("Changes Applied", "success")
            return redirect("/admin")
        except Exception as e:
            if CONFIG["DEBUG"]:
                raise e
            else:
                flash("Something went wrong.", "error")
    user = controller.get_user_by_id(uid)
    form.first_name.data = user.firstname
    form.last_name.data = user.lastname
    form.email.data = user.email
    form.roles.data = ",".join(user.roles)
    return render_template("admin.edit.html", user = user, form = form)

@cache.cached()
@mod_admin.route("/admin/delete", methods = ["GET", "POST"])
@login_required
@sentinel.admin.require(http_exception = 403)
def delete_member():
    if request.method == "POST":
        controller.delete_user(request.form["email"])
        flash("User Deleted", "success")
    return redirect("/admin")
