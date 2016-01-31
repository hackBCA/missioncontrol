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

  