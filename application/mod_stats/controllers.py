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

def get_review_stats():
  stats = []

  num_submitted = UserEntry.objects(type_account = "hacker", status = "Submitted").count()
  num_review0 = UserEntry.objects(type_account = "hacker", status = "Submitted", review1 = None).count()
  num_review1 = UserEntry.objects(type_account = "hacker", status = "Submitted", review1__in = [1, 2, 3, 4, 5], review2 = None).count()
  num_review2 = UserEntry.objects(type_account = "hacker", status = "Submitted", review2__in = [1, 2, 3, 4, 5], review3 = None).count()
  num_review3 = UserEntry.objects(type_account = "hacker", status = "Submitted", review3__in = [1, 2, 3, 4, 5]).count()

  stats.append('%d Submitted Apps' % num_submitted)
  stats.append('%d Apps reviewed 0 times' % num_review0)
  stats.append('%d Apps reviewed 1 time' % num_review1)
  stats.append('%d Apps reviewed 2 times' % num_review2)
  stats.append('%d Apps reviewed 3 times' % num_review3)

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

def get_rsvp_stats():
  stats = {}

  account_types = {"hacker": "Hacker", "mentor": "Mentors", "scholarship": "Scholarship"}

  for type_account in account_types:
    type_account_stats = []
    num_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account).count()

    type_account_stats.append("%d Attending" % (num_attending))
    if type_account in ["hacker", "scholarship"]:
      num_male_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, gender = "male").count()
      num_female_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, gender = "female").count()
      num_other_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, gender = "other").count()
      num_rns_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, gender = "rns").count()
      print(num_male_attending, num_attending)
      percent_male_attending = 0 if num_attending == 0 else 100.0 * num_male_attending / num_attending
      percent_female_attending = 0 if num_attending == 0 else 100.0 * num_female_attending / num_attending
      percent_other_attending = 0 if num_attending == 0 else 100.0 * num_other_attending / num_attending
      percent_rns_attending = 0 if num_attending == 0 else 100.0 * num_rns_attending / num_attending
    
      type_account_stats.append("%d%% Male (%d)" % (percent_male_attending, num_male_attending))
      type_account_stats.append("%d%% Female (%d)" % (percent_female_attending, num_female_attending))
      type_account_stats.append("%d%% Other (%d)" % (percent_other_attending, num_other_attending))
      type_account_stats.append("%d%% Rather Not Say (%d)" % (percent_rns_attending, num_rns_attending))

      num_beginner_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, beginner = "yes").count()
      num_nonbeginner_attending = UserEntry.objects(rsvp = True, attending = "Attending", type_account = type_account, beginner = "no").count()

      percent_beginner_attending = 0 if num_attending == 0 else 100.0 * num_beginner_attending / num_attending
      percent_nonbeginner_attending = 0 if num_attending == 0 else 100.0 * num_nonbeginner_attending / num_attending
      type_account_stats.append("%d%% Beginner (%d)" % (percent_beginner_attending, num_beginner_attending))
      type_account_stats.append("%d%% Non Beginner (%d)" % (percent_nonbeginner_attending, num_nonbeginner_attending))
    stats[account_types[type_account]] = type_account_stats
  return stats