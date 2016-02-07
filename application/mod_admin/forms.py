from wtforms import Form, TextField, PasswordField, SelectField, TextAreaField, BooleanField, validators, ValidationError, RadioField
import re

class StaffForm(Form):
	first_name = TextField("First Name", [
		validators.Required(message = "You must enter a first name.")
	], description = "First Name")

	last_name = TextField("Last Name", [
		validators.Required(message = "You must enter a last name.")
	], description = "Last Name")

	email = TextField("Email", [
		validators.Required(message = "Enter an email."),
		validators.Email(message = "Invalid email address.")
	], description = "Email")

	password = PasswordField("Password", [
		validators.Required(message = "You must enter a password.")
	], description = "Password")

	confirm_password = PasswordField("Confirm Password", description = "Confirm Password")

	roles = TextField("Role", [
		validators.Required(message = "Enter the roles of the account.")
	], description = "Roles")

	def validate_confirm_password(form, field):
		password = form['password'].data
		if password != field.data:
			raise ValidationError("Passwords must match.")

class StaffUpdateForm(Form):
	first_name = TextField("First Name", [
		validators.Required(message = "You must enter a first name.")
	], description = "First Name")

	last_name = TextField("Last Name", [
		validators.Required(message = "You must enter a last name.")
	], description = "Last Name")

	email = TextField("Email", [
		validators.Required(message = "Enter an email."),
		validators.Email(message = "Invalid email address.")
	], description = "Email")

	roles = TextField("Role", [
		validators.Required(message = "Enter what role you are.")
	], description = "Roles")
