from application import CONFIG, app
from .models import *
from application.mod_hacker.models import UserEntry

def get_application_stats():
  stats = []
  num_accounts = UserEntry.objects().count()
  num_accounts_confirmed = UserEntry.objects(confirmed = True).count()
  percent_accounts_confirmed = 100.0 * num_accounts_confirmed / num_accounts

  stats.append('%d Accounts' % num_accounts)
  stats.append('%d%% Accounts confirmed (%d)' % (percent_accounts_confirmed, num_accounts_confirmed))
  
  #Following statistics for all CONFIRMED accounts
  num_accounts_not_started = UserEntry.objects(confirmed = True, status = "Not Started").count()
  num_accounts_in_progress = UserEntry.objects(confirmed = True, status = "In Progress").count()
  num_accounts_submitted = UserEntry.objects(confirmed = True, status = "Submitted").count()

  percent_accounts_not_started = 100.0 * num_accounts_not_started / num_accounts_confirmed
  percent_accounts_in_progress = 100.0 * num_accounts_in_progress / num_accounts_confirmed
  percent_accounts_submitted = 100.0 * num_accounts_submitted / num_accounts_confirmed

  stats.append('%d%% Applications have status \"Not Started\" (%d)' % (percent_accounts_not_started, num_accounts_not_started))
  stats.append('%d%% Applications have status \"In Progress\" (%d)' % (percent_accounts_in_progress, num_accounts_in_progress))
  stats.append('%d%% Applications have status \"Submitted\" (%d)' % (percent_accounts_submitted, num_accounts_submitted))

  num_mentors = UserEntry.objects(confirmed = True, type_account = "mentor").count()

  stats.append('%d total mentors signed up.' % (num_mentors) )

  return stats

#Only for submitted
def get_applicant_stats():
  stats = []
  num_submitted = UserEntry.objects(status = "Submitted").count()
  num_hackers_accounts_submitted = UserEntry.objects(confirmed = True, status = "Submitted", type_account = "hacker").count()

  num_beginners = UserEntry.objects(confirmed = True, beginner = "yes", status = "Submitted", type_account = "hacker").count()
  num_males = UserEntry.objects(confirmed = True, gender = "male", status = "Submitted", type_account = "hacker").count()
  num_females = UserEntry.objects(confirmed = True, gender = "female", status = "Submitted", type_account = "hacker").count()
  num_rathernotsay = UserEntry.objects(confirmed = True, gender = "rns", status = "Submitted", type_account = "hacker").count()

  percent_accounts_beginners = 100.0 * num_beginners / num_hackers_accounts_submitted
  percent_accounts_female = 100.0 * num_females / num_hackers_accounts_submitted
  percent_accounts_male = 100.0 * num_males / num_hackers_accounts_submitted
  percent_accounts_rns = 100.0 * num_rathernotsay / num_hackers_accounts_submitted

  stats.append('%d%% Beginners (%d)' % (percent_accounts_beginners, num_beginners))
  stats.append('%d%% Female (%d)' % (percent_accounts_female, num_females))
  stats.append('%d%% Male (%d)' % (percent_accounts_male, num_males))
  stats.append('%d%% Rather Not Say (%d)' % (percent_accounts_rns, num_rathernotsay))

  return stats

def get_accepted_stats():
  stats = {}
     
  account_types = {"hacker": "Hackers", "mentor": "Mentors", "scholarship": "Scholarship"}
  for type_account in account_types:
    if type_account == "hacker":
      num_ready_accept = UserEntry.objects(status = "Submitted", type_account = type_account, review3__ne = None).count()
    else:
      num_ready_accept = UserEntry.objects(status = "Submitted", type_account = type_account).count()

    num_accepted = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Accepted").count()
    num_waitlisted = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Waitlisted").count()
    num_expired = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Expired").count()

    num_not_rsvped = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Accepted", rsvp__ne = True).count()
    num_attending = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Accepted", rsvp = True, attending = "Attending").count()
    num_not_attending = UserEntry.objects(status = "Submitted", type_account = type_account, decision = "Accepted", rsvp = True, attending = "Not Attending").count()

    percent_accepted = 0 if num_ready_accept == 0 else 100.0 * num_accepted / num_ready_accept
    percent_waitlisted = 0 if num_ready_accept == 0 else 100.0 * num_waitlisted / num_ready_accept
    percent_expired = 0 if num_ready_accept == 0 else 100.0 * num_expired / num_ready_accept    

    percent_not_rsvped = 0 if num_accepted == 0 else 100.0 * num_not_rsvped / num_accepted
    percent_attending = 0 if num_accepted == 0 else 100.0 * num_attending / num_accepted
    percent_not_attending = 0 if num_accepted == 0 else 100.0 * num_not_attending / num_accepted

    type_account_stats = []

    type_account_stats.append('%d Accept-able Users' % num_ready_accept)
    type_account_stats.append('%d%% Accepted (%d)' % (percent_accepted, num_accepted))
    type_account_stats.append('%d%% Waitlisted (%d)' % (percent_waitlisted, num_waitlisted))
    type_account_stats.append('%d%% Offer Expired (%d)' % (percent_expired, num_expired))
    type_account_stats.append('%d%% Not Yet Responded (%d)' % (percent_not_rsvped, num_not_rsvped))
    type_account_stats.append('%d%% Attending (%d)' % (percent_attending, num_attending))
    type_account_stats.append('%d%% Not Attending (%d)' % (percent_not_attending, num_not_attending))

    stats[type_account] = type_account_stats
  return stats
