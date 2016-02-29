from application import CONFIG, app
from .models import *
import sendgrid
import time
from itsdangerous import URLSafeTimedSerializer

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])
ts = URLSafeTimedSerializer(CONFIG["SECRET_KEY"])

def get_participant(email):
    entries = UserEntry.objects(email = email.lower())

    if entries.count() == 1:
        return entries[0]
    return None   

def get_next_application(reviewer_email):
    users = UserEntry.objects(status = "Submitted", review1 = None)
    if users.count():
        return users[0]
    users = UserEntry.objects(status = "Submitted", review2 = None, reviewer1__ne = reviewer_email)
    if users.count():
        return users[0]
    users = UserEntry.objects(status = "Submitted", review3 = None, reviewer1__ne = reviewer_email, reviewer2__ne = reviewer_email)
    if users.count():
        return users[0]
    return None

def review_application(email, review, reviewer):
    user = get_participant(email)
    for r in ["1","2","3"]:
        if not "review"+r in user or user["review"+r] not in [1, 2, 3, 4, 5]:
            user["review"+r] = review
            user["reviewer"+r] = reviewer 
            break
    user.save()

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