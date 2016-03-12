from flask import render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from . import stats_module as mod_stats
from . import controllers as controller
from .forms import *
from application import CONFIG

@mod_stats.route("/stats", methods=["GET", "POST"])
@login_required
#No specific permission required
def login():
  application_stats = controller.get_application_stats()
  applicant_stats = controller.get_applicant_stats()
  return render_template("stats.stats.html", application_stats = application_stats, applicant_stats = applicant_stats)
