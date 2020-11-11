from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
	
	username = StringField('Username',
							validators=[DataRequired(),Length(min=2,max=20)])
	# TO-DO: how to ensure that Username is unique? any class to check that across db?

	email = StringField('Email',
							validators=[DataRequired(),Email()])
	#TO-DO: Check for already used Email 

	password = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Password',validators=[DataRequired(),EqualTo('password')])

	submit	= SubmitField('Sign Up')


class LoginForm(FlaskForm):
	
	email = StringField('Email',
							validators=[DataRequired(),Email()])

	password = PasswordField('Password',validators=[DataRequired()])
	
	remember = BooleanField('Remember Me')

	submit	= SubmitField('Sign In')