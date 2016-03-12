from application import CONFIG, app
from .models import *
from flask import current_app, session
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, RoleNeed
import bcrypt
import re
import sendgrid
import time
from itsdangerous import URLSafeTimedSerializer

AuthenticationError = Exception("AuthenticationError", "Invalid credentials.")
UserExistsError = Exception("UserExistsError", "Email already exists in database.")
UserDoesNotExistError = Exception("UserDoesNotExistError", "Account with given email does not exist.")

login_manager = LoginManager()
login_manager.init_app(app)

principals = Principal(app)

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])
ts = URLSafeTimedSerializer(CONFIG["SECRET_KEY"])

@login_manager.user_loader
def load_user(user_id): 
  user_entries = StaffUserEntry.objects(id = user_id)
  if user_entries.count() != 1:
    return None
  currUser = user_entries[0]
  user = User(currUser.id, currUser.email, currUser.firstname, currUser.lastname, currUser.roles) 
  return user

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
  identity.user = current_user

  if hasattr(current_user, 'roles'):
    for role in current_user.roles:
      identity.provides.add(RoleNeed(role))

def get_user(email):
  entries = StaffUserEntry.objects(email = email)

  if entries.count() == 1:
    return entries[0]
  return None

def verify_user(email, password):
  currUser = get_user(email)

  if currUser is None:
    return None

  hashed = currUser.hashed    

  if bcrypt.hashpw(password.encode("utf-8"), hashed.encode("utf-8")) == hashed.encode("utf-8"):
    return load_user(currUser.id)
  else:
    return None

def login(email):
  user = load_user(get_user(email).id)

  if user != None:
    login_user(user)
    identity_changed.send(current_app._get_current_object(), identity = Identity(user.uid))
  else:
    raise UserDoesNotExistError

def logout():
  logout_user()
  
  for key in ('identity.name', 'identity.auth_type'):
    session.pop(key, None)

  identity_changed.send(current_app._get_current_object(), identity = AnonymousIdentity())

def tokenize_email(email):
  return ts.dumps(email, salt = CONFIG["EMAIL_TOKENIZER_SALT"])
def detokenize_email(token):
  return ts.loads(token, salt = CONFIG["EMAIL_TOKENIZER_SALT"], max_age = 86400)

def send_recovery_email(email):
  user = get_user(email)

  if user is None:
    raise UserDoesNotExistError

  token = tokenize_email(email)
  message = sendgrid.Mail()
  message.add_to(email)
  message.set_from("noreply@hackbca.com")
  message.set_subject("hackBCA III - Account Recovery")
  message.set_html("<p></p>")

  message.add_filter("templates", "enable", "1")
  message.add_filter("templates", "template_id", CONFIG["SENDGRID_ACCOUNT_RECOVERY_TEMPLATE"])
  message.add_substitution("token", token)  

  status, msg = sg.send(message)

def change_name(email, firstname, lastname):
  account = get_user(email)

  if account is None:
    raise UserDoesNotExistError

  account.firstname = firstname
  account.lastname = lastname
  account.save()

  login(email) #To update navbar

def change_password(email, password):
  account = get_user(email)

  if account is None:
    raise UserDoesNotExistError

  hashed = str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()))[2:-1]
  account.hashed = hashed
  account.save()

def get_user_attr(email, attr):
  user = get_user(email)

  if user is None:
    raise UserDoesNotExistError
  
  return getattr(user, attr)

def set_user_attr(email, attr, value):
  user = get_user(email)

  if user is None:
    raise UserDoesNotExistError
  
  setattr(user, attr, value)

  user.save()
