from flask import render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from flask.ext.principal import Principal, Permission, RoleNeed
from . import user_module as mod_user
from . import controllers as controller
from .forms import *
from application import CONFIG

admin_permission = Permission(RoleNeed("admin"))
test_permission = Permission(RoleNeed("test"))

@mod_user.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect("/")

  form = LoginForm(request.form)
  if request.method == "POST" and form.validate():
    try:
      if controller.verify_user(request.form["email"], request.form["password"]) is None:
        flash("Invalid email and/or password.", "error")
      else:
        controller.login(request.form["email"])
        return redirect("/account")
    except Exception as e:
      if(CONFIG["DEBUG"]):
        raise e
      else:
        flash("Something went wrong.", "error")

  return render_template("user.login.html", form = form)

@mod_user.route("/logout", methods=["GET", "POST"])
def logout():
  controller.logout()
  return redirect("/")

@mod_user.route("/forgot", methods = ["GET", "POST"])
@test_permission.require(http_exception = 403)
def recover():
  form = EmailForm(request.form)
  if request.method == "POST" and form.validate():
    try:
      controller.send_recovery_email(request.form["email"])
      flash("Email sent to " + request.form["email"] + '.', 'success')
    except Exception as e:
      exceptionType = e.args[0]
      if exceptionType == "UserDoesNotExistError":
        flash("No account exists with that email.", "error")
      else:
        if CONFIG["DEBUG"]:
          raise e
        else:
          flash("Something went wrong." , "error")
  return render_template("user.forgot.html", form = form)

@mod_user.route("/recover/<token>", methods = ["GET", "POST"])
def recover_change(token):
  email = controller.detokenize_email(token)

  form = RecoverForm(request.form)
  if request.method == "POST" and form.validate():
    try:
      controller.change_password(email, request.form["password"])
      flash("Password changed.", "sucess")
      return redirect("/")
    except Exception as e:
      if CONFIG["DEBUG"]:
        raise e
      else:
        flash("Something went wrong.", "error")
  return render_template("user.recover.html", email = email, form = form)

@mod_user.route("/account", methods = ["GET", "POST"])
#@login_required
def account():
  name_form = ChangeNameForm(request.form)
  password_form = ChangePasswordForm(request.form)

  if request.method == "POST":    
    if request.form["setting"] == "name" and name_form.validate():
      try:
        controller.change_name(current_user.email, request.form["firstname"], request.form["lastname"])
        flash("Name changed.", "success")
      except Exception as e:
        if CONFIG["DEBUG"]:
          raise e
        else:
          flash("Something went wrong.", "error")
    if request.form["setting"] == "password" and password_form.validate():
      if controller.verify_user(current_user.email, request.form["password"]) is not None:
        try:
          controller.change_password(current_user.email, request.form["new_password"])
          flash("Password changed.", "success")
        except Exception as e:
          if CONFIG["DEBUG"]:
            raise e
          else:
            flash("Something went wrong.", "error")
      else:
        flash("Incorrect password.", "error")
    if request.form["setting"] == "type_account":
      if current_user.status == "Submitted":
        flash("Application already submitted.", "error")
      else:
        try:
          controller.change_account_type(current_user.email, request.form["type_account"])
          flash("Account type changed.", "success")
        except Exception as e:
          if CONFIG["DEBUG"]:
            raise e
          else:
            flash("Something went wrong.", "error")

  user = controller.get_user(current_user.email)
  name_form = ChangeNameForm(obj = user)

  return render_template("user.settings.html", name_form = name_form, password_form = password_form)

