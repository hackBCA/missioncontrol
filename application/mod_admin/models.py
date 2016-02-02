from flask.ext.login import LoginManager, UserMixin
from mongoengine import *

class StaffUserEntry(Document):
	email = StringField(required = True)

	hashed = StringField(required = True)

	roles = ListField(required = True)
	
	firstname = StringField(required = True)
	lastname = StringField(required = True)

	def full_name(self):
		return self.firstname + " " + self.lastname
