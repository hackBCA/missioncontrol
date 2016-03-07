from application import CONFIG, app
from application.mod_user.models import *
from application.mod_user.controllers import get_user
import re
import sendgrid
import bcrypt
import time

UserExistsError = Exception("UserExistsError", "Email already exists in database")

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])

def get_users():
    entries = StaffUserEntry.objects()
    return entries

def add_user(email, firstname, lastname, password, roles):
  existingUser = get_user(email)
  if existingUser is not None:
    raise UserExistsError
  
  hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
  new_entry = StaffUserEntry(email = email, hashed = hashed, firstname = firstname, lastname = lastname, roles = roles)
  new_entry.save()

def edit_user(firstname, lastname, email, roles):
    existingUser = get_user(email)
    existingUser.firstname = firstname
    existingUser.lastname = lastname
    existingUser.email = email
    existingUser.roles = roles
    existingUser.save()

def delete_user(email):
    existingUser = get_user(email)
    existingUser.delete()

def get_user_by_id(uid):
    entries = StaffUserEntry.objects(id = uid)

    if entries.count() == 1:
        return entries[0]
    return None