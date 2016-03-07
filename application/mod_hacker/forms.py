from wtforms import Form, IntegerField, TextField, SelectField, validators, ValidationError

class RateForm(Form):
  rating = IntegerField("Rating", [validators.Required(message = "Please enter a rating.")])

account_type_choices = [
    ("", "Account Type"),
    ("hacker", "Hackers"),
    ("mentor", "Mentors")
]

class AcceptForm(Form):
  type_account = SelectField("Applicant Type", [validators.Required(message = "Please select the type of applicant you would like to accept.")], choices = account_type_choices, description = "Applicant Type")
  block_size = IntegerField("Block Size", [validators.Required(message = "Please enter the number of participants you would like to accept.")], description = "Block Size")