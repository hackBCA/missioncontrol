from flask import render_template, redirect, request, flash, session
from flask.ext.login import login_required, current_user
from . import admin_module as mod_admin
from . import controllers as controller
from application import CONFIG

