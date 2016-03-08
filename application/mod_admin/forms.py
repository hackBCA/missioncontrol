from wtforms import Form, TextField, PasswordField, SelectField, TextAreaField, \
    BooleanField, validators, ValidationError, RadioField, SelectMultipleField, \
    widgets
import re

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

role_choices = [
    ("organizer", "Organizer"),
    ("reviewer", "Reviewer"),
    ("admin", "Admin")
]

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

    roles = MultiCheckboxField("Roles", description = "Roles", choices = role_choices)

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

    roles = MultiCheckboxField("Roles", description = "Roles", choices = role_choices)
