from application import CONFIG, app
from application.mod_user.models import *
from application.mod_user.controllers import get_user, add_user
import re
import sendgrid
import bcrypt
import time

UserExistsError = Exception("UserExistsError", "Email already exists in database")

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])

def get_users():
	entries = StaffUserEntry.objects()
	return entries

def edit_user(firstname, lastname, email, roles):
	existingUser = get_user(email)
	existingUser.firstname = firstname
	existingUser.lastname = lastname
	existingUser.email = email
	existingUser.roles = [x.strip() for x in roles.split(',')]
	existingUser.save()

def delete_user(email):
	existingUser = get_user(email)
	existingUser.delete()