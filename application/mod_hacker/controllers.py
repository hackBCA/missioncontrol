from application import CONFIG, app
from .models import *
import sendgrid
import time
from itsdangerous import URLSafeTimedSerializer

def get_participants(page_num = 0, page_size = 50):
    users = UserEntry.objects(confirmed = True).skip((page_num + 1) * page_size).limit(page_size)
    return users

def summarize_participants(participants):
    status_map = {
    "Not Started": "NS",
    "In Progress": "IP",
    "Submitted": "S"
    }

    participants = [{
    'id':           str(person.id),
    'firstname':    person.firstname,
    'lastname':     person.lastname,
    'email':        person.email,
    'type_account': person.type_account[0].upper(),
    'status':       status_map[person.status],
    'school':       person.school if person.school is not None else ''
      }
    for person in participants]
    return participants


def get_participant(email):
    user = UserEntry.objects(email = email.lower())

    if entries.count() == 1:
        return entries[0]
    return None

def check_in(email):
    user = get_participant(email)

    #user.checked_in = True
    #user.save()

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])
ts = URLSafeTimedSerializer(CONFIG["SECRET_KEY"])

def get_applicant_by_id(uid):
  applicant_entries = UserEntry.objects(id = uid)
  if applicant_entries.count() != 1:
    return None
  applicant = applicant_entries[0]
  return applicant

def get_applicant_dict(uid):
  applicant = get_applicant_by_id(uid)
  applicant = {k: applicant[k] for k, _ in applicant._fields.items()}
  applicant.pop("hashed", None)
  return applicant

def tokenize_email(email):
  return ts.dumps(email, salt = CONFIG["EMAIL_TOKENIZER_SALT"])

def send_unconfirmed_email():
  users = UserEntry.objects(confirmed = False)
  for u in users:
    email = u.email
    token = tokenize_email(email)
   
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Confirm your account!")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_ACCOUNT_NOT_YET_CONFIRMED_TEMPLATE"])
    message.add_substitution("token", token)  
    
    #status, msg = sg.send(message)
    print(email, status, msg)

def send_not_started_email():
  users = UserEntry.objects(status = "Not Started")
  for u in users:
    email = u.email
    
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Start your application!")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_APPLICATION_NOT_STARTED_TEMPLATE"])
    
    #status, msg = sg.send(message)
    #print(email, status, msg)

def send_in_progress_email():
  users = UserEntry.objects(status = "In Progress")
  for u in users:
    email = u.email

    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Finish your application!")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_APPLICATION_IN_PROGRESS_TEMPLATE"])
    #status, msg = sg.send(message)
    #print(email, status, msg)