from application import CONFIG, app
from .models import *
from flask.ext.login import current_user
import sendgrid

import twilio
from twilio.rest import TwilioRestClient

import time
from itsdangerous import URLSafeTimedSerializer
from application.mod_stats.controllers import get_accepted_stats
import json
import os
import random

sg = sendgrid.SendGridClient(CONFIG["SENDGRID_API_KEY"])
ts = URLSafeTimedSerializer(CONFIG["SECRET_KEY"])

UserDoesNotExistError = Exception("UserDoesNotExistError", "Account with given email does not exist.")

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
    decision_map = {
        None: "&nbsp;",
        "Accepted": "A",
        "Waitlisted": "W",
        "Expired": "E"
    }    
    rsvp_map = {
        None: "Error",
        "Undecided": "U",
        "Attending": "A",
        "Not Attending": "NA"
    }

    summary = [{
    "id":           str(person.id),
    "name":         person.firstname + " " + person.lastname,
    "email":        person.email,
    "type_account": person.type_account[0].upper(),
    "status":       status_map[person.status],
    "school":       person.school if not person.school in ("", None) else "&nbsp;",
    "decision":     decision_map[person.decision],
    "rsvp":         "&nbsp;" if person.decision != "Accepted" else rsvp_map["Undecided" if not person.rsvp else person.attending],
    "checkedin":    "&nbsp;" if not person.rsvp or person.attending != "Attending" else ("Y" if person.checked_in else "N")
      }
    for person in participants]

    return summary

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

def set_user_attr(user, attr, value):
    setattr(user, attr, value)
    user.save()

def get_next_application(reviewer_email):
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", decision = None, review1 = None)
    if users.count():
        return users[random.randint(0, users.count() - 1)]
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", decision = None,  review2 = None, reviewer1__ne = reviewer_email)
    if users.count():
        return users[random.randint(0, users.count() - 1)]
    users = UserEntry.objects(status = "Submitted", type_account = "hacker", decision = None,  review3 = None, reviewer1__ne = reviewer_email, reviewer2__ne = reviewer_email)
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

def expire_applicants(type_account, block_size):
    if type_account == "mentor":
        return "0 mentors expired."

    bad_time = int(time.time()) - 7 * 24 * 60 * 60 #How to break your iPhone 101
    users = UserEntry.objects(rsvp__ne = True, type_account = type_account, decision = "Accepted", accepted_time__lte = bad_time).order_by("accepted_time")

    if len(users) > block_size:
        users = users[:block_size]
 
    for user in users:
        user.decision = "Expired"
        user.rsvp = True
        if not CONFIG["DEBUG"]:
            user.save()
    return str(len(users)) + " " + type_account + "s expired."
 
def accept_applicants(type_account, block_size):    
    if type_account == "hacker":
        user_pool = UserEntry.objects(status = "Submitted", type_account = type_account, review3__ne = None, decision__nin = ["Accepted", "Expired"])
        user_pool = sorted(user_pool, key = lambda k: k["review1"] + k["review2"] + k["review3"], reverse = True)
        user_pool = sorted(user_pool, key = lambda k: 0 if k["gender"] in ["female", "other"] else 1)

        total_beginner = 0
        for user in user_pool:
            if user["beginner"] == "yes":
                total_beginner += 1
        total_non_beginner = len(user_pool) - total_beginner

        total_target = block_size
        target_beginner = int(block_size * .6)
        accepted_non_male = 0
        accepted_beginner = 0

        accepted_users = []

        for user in user_pool:
            if total_target == 0:
                break

            accept_user = False

            if user["beginner"] == "yes":
                if accepted_beginner < target_beginner or len(accepted_users) - accepted_beginner == total_non_beginner: #Second clause in case we run out of non-beginners:
                    accept_user = True
                    accepted_beginner += 1            
            else:
                accept_user = True
    
            if user["gender"] in ["female", "other"]:
                accepted_non_male += 1

            if accept_user:
                accepted_users.append(user)
                total_target -= 1
    if type_account == "mentor":
        user_pool = UserEntry.objects(status = "Submitted", type_account = type_account, decision__nin = ["Accepted", "Expired"])
        accepted_users = user_pool[:block_size]
    
    for user in accepted_users:
        accept_applicant(user)  
    return str(len(accepted_users)) + " " + type_account + "s accepted."   

def accept_applicant(user):
    user.decision = "Accepted"
    user.accepted_time = int(time.time())
    user.rsvp = False
    if not CONFIG["DEBUG"]:
        user.save()
        send_accepted_email(user['email'], user['type_account'])
    
def waitlist_applicants(type_account, block_size):
    if type_account == "hacker" or type_account == "scholarship":
        users = UserEntry.objects(status = "Submitted", type_account = type_account, review3__ne = None, decision__nin = ["Accepted", "Waitlisted", "Expired"]).limit(block_size)

        for user in users:
            user.decision = "Waitlisted"
            if not CONFIG["DEBUG"]:
                user.save()
                send_waitlisted_email(user['email'], user['type_account'])
        return str(len(users)) + " hackers waitlisted."
    if type_account == "mentor":
        return 0 + " mentors waitlisted."        

def send_waitlisted_email(email, type):
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Account Status Update")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_WAITLISTED_TEMPLATE"])

    status, msg = sg.send(message)

def send_accepted_email(email, type_account):
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - You're in!")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    if type_account == "mentor":
        message.add_filter("templates", "template_id", CONFIG["SENDGRID_MENTOR_ACCEPTED_TEMPLATE"])
    elif type_account == "scholarship":
        message.add_filter("templates", "template_id", CONFIG["SENDGRID_SCHOLARSHIP_ACCEPTED_TEMPLATE"])
    else:
        message.add_filter("templates", "template_id", CONFIG["SENDGRID_ACCEPTED_TEMPLATE"])

    status, msg = sg.send(message)

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
  users = UserEntry.objects(confirmed = True, status = "Not Started")
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
    print(email, status, msg)

def send_in_progress_email():
  users = UserEntry.objects(confirmed = True, status = "In Progress")
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
    print(email, status, msg)

def send_generic_template_email(to, subject, body):
    message = sendgrid.Mail()
    message.add_to(to)
    message.set_from("contact@hackbca.com")
    message.set_subject(subject)
    message.set_html(body)

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_GENERIC_TEMPLATE"])

    status, msg = sg.send(message)
    return status, msg

def rsvp_problem_notify():
  users = UserEntry.objects(decision = "Accepted", rsvp = True, attending = None)
  for u in users:
    u.rsvp = False
    u.save()
    print(u['email'], send_generic_template_email(u['email'], "hackBCA III - Technical Error (Please read!)", CONFIG["RSVP_PROBLEM_BODY"]))

def rsvp_final_reminder():
    users = UserEntry.objects(decision = "Accepted", rsvp__ne = True)
    for u in users:
        print(u['email'], send_generic_template_email(u['email'], "hackBCA III - You still need to rsvp!", CONFIG["RSVP_FOLLOW_UP_BODY"]))

def send_participant_info_emails():
    users = UserEntry.objects(decision = "Accepted", rsvp = True, attending = "Attending", type_account__in = ["hacker", "scholarship"])
    for u in users:
        print(u['email'], u['type_account'])
        message = sendgrid.Mail()
        message.add_to(u.email)
        message.set_from("contact@hackbca.com")
        message.set_subject("hackBCA III - Important information")
        message.set_html("<p></p>")

        message.add_substitution("[[name]]", u.firstname)
        message.add_filter("templates", "enable", "1")
        message.add_filter("templates", "template_id", CONFIG["SENDGRID_HACKER_INFORMATION_TEMPLATE"])

        #status, msg = sg.send(message)
        print(u.email, status, msg)

def send_mentor_info_emails():
    users = UserEntry.objects(decision = "Accepted", rsvp = True, attending = "Attending", type_account = "mentor")
    for u in users:
        r = send_mentor_info_email(u)
        print(u['email'], r)

def send_mentor_info_email(u):        
    message = sendgrid.Mail()
    message.add_to(u.email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Important information")
    message.set_html("<p></p>")

    message.add_substitution("[[name]]", u.firstname)
    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_MENTOR_INFORMATION_TEMPLATE"])

    status, msg = sg.send(message)
    return (status, msg)


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
    user.check_in_log.append([checked_in, int(time.time()), current_user.email])
    user.save()
    
twilio_client = twilio.rest.TwilioRestClient(CONFIG["TWILIO_SID"], CONFIG["TWILIO_AUTH_TOKEN"])

def sendTextMessage(body, to):
    msg = twilio_client.messages.create(body = body, to = to, from_ = "+12012214142")

def sms_blast(type_accounts, message):
    phoneNums = []
    if len(type_accounts) == 1 and type_accounts[0] == "staff":
        phoneNums = get_staff_phone_nums()
    else:
        users = UserEntry.objects(checked_in = True, type_account__in = type_accounts, smsblast_optin = True)
        for u in users:
            phoneNums.append(u['phone'])
        
    sent, failed = 0, 0
    for phone in phoneNums:
        try:
            sendTextMessage(message, phone)  
            sent += 1
        except Exception as e:
            if CONFIG["DEBUG"]:
                raise e
            failed += 1
            pass
    return (sent, failed)

def get_staff_phone_nums():
    try:
        csv = open(os.path.join("ignore/", CONFIG["STAFF_CONTACT_INFO_FILE"]), "r")
        fields = csv.readline().split(",")
        data = [d.split(",") for d in csv.read().split("\n")]    
        csv.close()

        phonePos = fields.index("Phone") 
    except Exception as e:
        raise Exception("CsvException", "Missing CSV File")
    phoneNums = []
    for d in data:
        if phonePos < len(d):
            print(d)
            phoneNums.append(d[phonePos])
    return phoneNums

def get_path_participants():
    path_dict = {
        "code-for-good": "Code for Good",
        "ios": "iOS",
        "web-dev": "Web Development"
    }

    users = UserEntry.objects(path__ne = None)
    participants = [{
        'id':           str(u.id),
        'name':         u.firstname + ' ' + u.lastname,
        'email':        u.email,
        'path':         path_dict[u.path],
        'checkedin':    "Y" if u.checked_in else "N"
    } for u in users]

    return participants

def get_app_setting(setting):
    settings = AppSettings.objects()[0]
    return getattr(settings, setting)

def set_app_setting(setting, value):
    settings = AppSettings.objects()[0]
    setattr(settings, setting, value)
    settings.save()