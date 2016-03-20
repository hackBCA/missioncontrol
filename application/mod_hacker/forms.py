from wtforms import Form, IntegerField, TextField, TextAreaField, SelectField, SelectMultipleField, validators, ValidationError

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

sms_blast_account_type_choices = [
    ("hacker", "Hackers"),
    ("scholarship", "Scholarship"),
    ("mentor", "Mentors")
]

class SmsBlastForm(Form):
  type_accounts = SelectMultipleField("Account Type", [validators.Required(message = "Please select at least one group to text.")], choices = sms_blast_account_type_choices, description = "Account Type")
  message = TextAreaField("Message", [validators.Required(message = "Enter a message."), validators.Length(max = 160, message = "Your message may be no more than 160 characters.")], description = "Message")