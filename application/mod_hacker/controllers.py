from application import CONFIG, app
from .models import *
import sendgrid
import time
from itsdangerous import URLSafeTimedSerializer
import random
import json, os

def sse_load_participants():
    SSE_BUFFER = 50
    page = 0
    chunk = get_all_accounts_paginate(page, SSE_BUFFER)
    while len(chunk) != 0:
        summarized = summarize_participants(chunk)
        page += 1
        event = ServerSSEEvent(str(json.dumps(summarized)), "chunk")
        yield event.encode()
        chunk = get_all_accounts_paginate(page, SSE_BUFFER)
    event = ServerSSEEvent(" ", "stop")
    yield event.encode()

def ajax_load_participants():
    accounts = get_all_accounts()
    summarized = summarize_participants(accounts)
    return summarized

def get_all_accounts():
    accounts = UserEntry.objects()
    return accounts

def get_all_accounts_paginate(page, buffer_size):
    accounts = UserEntry.objects().skip(page * buffer_size).limit(buffer_size)
    return accounts

def summarize_participants(participants):
    status_map = {
    "Not Started": "NS",
    "In Progress": "IP",
    "Submitted": "S"
    }

    summary = [{
    "id":           str(person.id),
    "name":         person.firstname + " " + person.lastname,
    "email":        person.email,
    "type_account": person.type_account[0].upper(),
    "status":       status_map[person.status],
    "school":       person.school if not person.school in ("", None) else "&nbsp;"
      }
    for person in participants]

    return summary

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
  applicant.pop("id", None)
  return applicant

def get_participant(email):
    entries = UserEntry.objects(email = email.lower())

    if entries.count() == 1:
        return entries[0]
    return None   

def get_next_application(reviewer_email):
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", review1 = None)
    if users.count():
        return users[random.randint(0, users.count() - 1)]
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", review2 = None, reviewer1__ne = reviewer_email)
    if users.count():
        return users[random.randint(0, users.count() - 1)]
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", review3 = None, reviewer1__ne = reviewer_email, reviewer2__ne = reviewer_email)
    if users.count():
        return users[random.randint(0, users.count() - 1)]
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

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit(".", 1)[1] in allowed_extensions

def process_waiver_file(filename):
    try:
        csv = open(os.path.join(CONFIG["UPLOAD_FOLDER"], filename), "r")
        fields = csv.readline().split(",")
        data = [d.split(",") for d in csv.read().split("\n")]    
        csv.close()
        os.remove(os.path.join(CONFIG["UPLOAD_FOLDER"], filename))

        emailPos = fields.index("email") 
    except Exception as e:
        raise Exception("CsvException", "Invalid CSV File")
    
    emails = [d[emailPos] for d in data]
    users = UserEntry.objects(email__in = emails)
    users_updated = 0
    for user in users:
        if user.waiver != True:
            users_updated += 1
        user.waiver = True
        user.save() 
    return users_updated

def check_in_status_user(user, checked_in): 
    if user.attending != "Attending":
        return
    user.checked_in = checked_in
    user.save()