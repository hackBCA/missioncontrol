from mongoengine import *

#Mongo Object
class UserEntry(Document):
  meta = {"strict" : False }

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

  intended_major = StringField()
  other_intended_major = StringField()

  reduced_lunch = StringField()

  hear_about_us = StringField()
  other_hear_about_us = StringField()

  free_response1 = StringField() #Mentor: Phone Number
  free_response2 = StringField() #Mentor: Skills
  free_response3 = StringField() #Mentor: Workshop

  mlh_terms = StringField()

  review1 = IntField()
  reviewer1 = StringField()
  review2 = IntField()
  reviewer2 = StringField()
  review3 = IntField()
  reviewer3 = StringField()

  attending = StringField()
  phone = StringField()
  t_shirt_size = StringField()

  emergency_contact_name1 = StringField()
  emergency_contact_phone1 = StringField()
  emergency_contact_relation1 = StringField()

  emergency_contact_name2 = StringField()
  emergency_contact_phone2 = StringField()
  emergency_contact_relation2 = StringField()

  food_allergies = StringField()
  medical_information = StringField()
  hackbca_rules = StringField()

  decision = StringField()
  accepted_time = IntField()
  attending = StringField()
  rsvp = BooleanField(default = False) #Has the user submitted their rsvp form?

  waiver = BooleanField(default = False)
  checked_in = BooleanField(default = False)

  meta = {"strict" : False }

class ServerSSEEvent(object):
    """Object wrapper for Server-Sent Event communication with clients.
    Arguments:
        data: data to be passed to client.
        event: event name that clients can use to distinguish different actions.
        id: identification for instance of object.
        desc_map: maps arguments to attributes expected by client.
    """
    def __init__(self, data, event):
        self.data = data
        self.event = event
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        """Encodes object into format that client will be expecting."""
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.items() if k]
        return "%s\n\n" % "\n".join(lines)
