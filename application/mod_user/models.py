from flask.ext.login import LoginManager, UserMixin
from mongoengine import *
from application.mod_admin.permissions import roles as all_roles

#Mongo Object
class StaffUserEntry(Document):
  email = StringField(required = True)
  hashed = StringField(required = True)

  roles = ListField(required = True)

  firstname = StringField(required = True)
  lastname = StringField(required = True)

  def full_name(self):
    return self.firstname + " " + self.lastname

  roles = ListField(required = False)

class User(UserMixin):
  def __init__(self, uid, email, firstname, lastname, roles):

    self.uid = str(uid)
    self.email = email
    self.firstname = firstname
    self.lastname = lastname
    if "admin" in roles:
      self.roles = all_roles
    else:
      self.roles = roles

  def get_navbar(self):
    navbar = [
      ("/", "Home"),
      ("/stats", "Statistics")]
     
    if "read_data" in self.roles:
      navbar.append(("/search", "Search"))   
    if "review_apps" in self.roles:
      navbar.append(("/review", "Review Apps"))
    if "board" in self.roles:
      navbar.append(("/waivers", "Update Waivers"))
    if "director" in self.roles:
      navbar.append(("/accept", "Accept Applicants"))
    if "sms_blast" in self.roles:
      navbar.append(("/smsblast", "SMS Blast"))
    if "paths" in self.roles:
      navbar.append(("/paths", "Paths Program"))
    if "broadcast" in self.roles:
      navbar.append(("/broadcast", "Broadcast"))
    if "admin" in self.roles:
      navbar.append(("/admin", "Admin"))

    navbar.append(("/account", "Settings"))

    return navbar 

  def is_authenticated(self):
    return True

  def get_id(self):
    return self.uid

  def full_name(self):
    return self.firstname + " " + self.lastname

#HACKATHON PARTICIPANTS
class UserEntry(Document):
  email = StringField(required = True)
  hashed = StringField(required = True)

  firstname = StringField(required = True)
  lastname = StringField(required = True) 

  confirmed = BooleanField(required = False, default = False)

  status = StringField(default = "Not Started")
  # In Progress, Submitted, Accepted, Waitlist

  type_account = StringField(required = True, default = "hacker")

  school = StringField()
  gender = StringField()
  beginner = StringField()
  ethnicity = StringField()
  grade = StringField()
  num_hackathons = StringField()
  
  phone = StringField()

  github_link = StringField()
  linkedin_link = StringField()
  site_link = StringField()
  other_link = StringField()

  free_response1 = StringField() #Mentor: Phone Number
  free_response2 = StringField() #Mentor: Skills
  free_response3 = StringField() #Mentor: Workshop  

  mlh_terms = StringField() 