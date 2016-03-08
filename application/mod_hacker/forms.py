from wtforms import Form, IntegerField, validators, ValidationError

class RateForm(Form):
    rating = IntegerField("Rating", [validators.Required(message = "Please enter a rating.")])
  