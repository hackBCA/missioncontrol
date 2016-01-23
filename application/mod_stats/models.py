from flask.ext.login import LoginManager, UserMixin
from mongoengine import *

#Mongo Object
class StaffUserEntry(Document):
  email = StringField(required = True)
  hashed = StringField(required = True)

  firstname = StringField(required = True)
  lastname = StringField(required = True) 

class User(UserMixin):
  def __init__(self, uid, email, firstname, lastname):

    self.uid = str(uid)
    self.email = email
    self.firstname = firstname
    self.lastname = lastname

  def is_authenticated(self):
    return True

  def get_id(self):
    return self.uid

  def full_name(self):
    return self.firstname + " " + self.lastname
