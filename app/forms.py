from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError

#Forms
class RegisterForm(FlaskForm):
    username = StringField(label='Username: ', validators=[Length(min=4, max=40), DataRequired()])
    email = StringField(label='Email: ', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password: ', validators=[Length(min=8), DataRequired()])
    password2 = PasswordField(label='Confirm password: ', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='Username: ', validators=[Length(min=4, max=40), DataRequired()])
    password = PasswordField(label='Password: ', validators=[Length(min=8), DataRequired()])
    submit = SubmitField(label='Log in')

class EmailForm(FlaskForm):
    email = StringField(label='Email: ', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Submit')

class ResetForm(FlaskForm):
    code = StringField(label='Code: ', validators=[DataRequired()])
    username = StringField(label='Username: ', validators=[Length(min=4, max=40), DataRequired()])
    password1 = PasswordField(label='Password: ', validators=[Length(min=8), DataRequired()])
    password2 = PasswordField(label='Confirm password: ', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Submit')