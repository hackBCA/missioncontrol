from application import CONFIG, app
from .models import *
import re
import sendgrid
import bcrypt
import time

UserExistsError = Exception("UserExistsError", "Email already exists in database")

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])

def get_users():
	entries = StaffUserEntry.objects()
	return entries

def get_user(email):
	entries = StaffUserEntry.objects(email = email.lower())

	if entries.count() == 1:
		return entries[0]
	return None

def add_user(firstname, lastname, email, password, roles):
	existingUser = get_user(email)
	if existingUser is not None:
		raise UserExistsError

	hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
	new_entry = StaffUserEntry(email = email.lower(), hashed = hashed, firstname = firstname, lastname = lastname, roles = [x.strip() for x in roles.split(',')])
	new_entry.save()

	#implement later
	#validate_email(email)

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