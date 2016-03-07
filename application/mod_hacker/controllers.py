from application import CONFIG, app
from .models import *
import sendgrid
import time
from itsdangerous import URLSafeTimedSerializer
from application.mod_stats.controllers import get_accepted_stats

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

def expire_applicants():
    bad_time = int(time.time()) - 7 * 24 * 60 * 60 #How to break your iPhone 101
    users = UserEntry.objects(rsvp__ne = True, decision = "Accepted", accepted_time__lte = bad_time) 
    for user in users:
        user.decision = "Expired"
        user.save()

def accept_applicants(type_account, block_size):
    expire_applicants()

    user_pool = UserEntry.objects(status = "Submitted", type_account = type_account, review3__ne = None, decision__nin = ["Accepted", "Expired"])
    user_pool = sorted(user_pool, key = lambda k: k["review1"] + k["review2"] + k["review3"], reverse = True)

    if type_account == "hacker":
        user_pool = sorted(user_pool, key = lambda k: 0 if k["gender"] in ["female", "other"] else 1)

        total_beginner = 0
        for i in range(0, len(user_pool)):
            print(user_pool[i]["email"], user_pool[i]["gender"], user_pool[i]["beginner"], user_pool[i]["review1"] + user_pool[i]["review2"] + user_pool[i]["review3"])
            if user_pool[i]["beginner"] == "yes":
                total_beginner += 1
        total_non_beginner = len(user_pool) - total_beginner

        total_target = block_size
        target_beginner = int(block_size * .6)
        accepted_non_male = 0
        accepted_beginner = 0

        accepted_users = []

        for i in range(0, len(user_pool)):
            if total_target == 0:
                break
            user = user_pool[i]

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
        accepted_users = user_pool[:block_size]
    
    for user in accepted_users:
        user.decision = "Accepted"
        user.accepted_time = int(time.time())
        print(user.decision, user.accepted_time)
        if not CONFIG["DEBUG"]:
            user.save()
            send_accepted_email(user['email'])     
    return str(len(accepted_users)) + " " + type_account + "s accepted."   

def waitlist_applicants(type_account, block_size):
    if type_account == "hacker":
        users = UserEntry.objects(status = "Submitted", type_account = type_account, review3__ne = None, decision__nin = ["Accepted", "Waitlisted", "Expired"])[:block_size]
        for user in users:
            user.decision = "Waitlisted"
            if not CONFIG["DEBUG"]:
                user.save()
                send_waitlisted_email(user['email'])
        return str(len(users)) + " hackers waitlisted."
    if type_account == "mentor":
        return 0 + " mentors Waitlisted."        

def send_waitlisted_email(email):
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - Account Status Update")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
    message.add_filter("templates", "template_id", CONFIG["SENDGRID_WAITLISTED_TEMPLATE"])

    status, msg = sg.send(message)

def send_accepted_email(email):
    message = sendgrid.Mail()
    message.add_to(email)
    message.set_from("contact@hackbca.com")
    message.set_subject("hackBCA III - You're in!")
    message.set_html("<p></p>")

    message.add_filter("templates", "enable", "1")
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