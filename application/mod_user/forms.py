from wtforms import Form, TextField, PasswordField, SelectField, TextAreaField, BooleanField, validators, ValidationError

class LoginForm(Form):
    email = TextField("Email", [
        validators.Required(message = "Enter an email."),
        validators.Email(message = "Invalid email address."
    )], description = "Email")
    password = PasswordField("Password", [], description = "Password")

class EmailForm(Form):
    email = TextField("Email", [
        validators.Required(message = "Enter an email."),
        validators.Email(message = "Invalid email address."
    )], description = "Email")

class RecoverForm(Form):
    password = PasswordField("Password", [
        validators.Required(message = "You must enter a password."),
        validators.Length(min = 8, message = "Password must be at least 8 characters.")
    ], description = "Password")
    confirm_password = PasswordField("Confirm Password", description = "Confirm Password")

    def validate_confirm_password(form, field):
        password = form['password'].data
        if len(password) >= 8 and password != field.data:
            raise ValidationError("Passwords must match.")

class ChangeNameForm(Form):
    firstname = TextField("First Name", [
        validators.Required(message = "You must enter a first name.")
    ], description = "First Name")
    lastname = TextField("Last Name", [
        validators.Required(message = "You must enter a last name.")
    ], description = "Last Name")

class ChangePasswordForm(Form):
    password = PasswordField("Password", [
        validators.Required(message = "You must enter your current password.")
    ], description = "Password")

    new_password = PasswordField("New Password", [
        validators.Required(message = "You must choose a new password."),
        validators.Length(min = 8, message = "Password must be at least 8 characters.")
    ], description = "New Password")
    confirm_password = PasswordField("Confirm New Password", description = "Confirm New Password")

    def validate_confirm_password(form, field):
        password = form['new_password'].data
        if len(password) >= 8 and password != field.data:
            raise ValidationError("Passwords must match.")