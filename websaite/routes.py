from flask import render_template, url_for, flash, redirect, request, abort
from websaite import app, db, bcrypt, mail
from websaite.forms import RegistrationForm, LoginForm, BirthdayForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from websaite.models import User, Record
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/about")
def about():
	return render_template('about.html',title='About')

@app.route("/register",methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data,email=form.email.data,password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account Created! You are now able to login','success')
		return redirect(url_for('login'))
	return render_template('register.html',title='Register', form=form)

@app.route("/login",methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user,remember = form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password','danger')
	return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account",methods = ['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username=form.username.data
		current_user.email=form.email.data
		db.session.commit()
		flash('Your account has been updated','success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html',title='Account',form=form)

@app.route("/birthdaylist/new",methods=['GET','POST'])
@login_required
def birthdaylist_new():
	form = BirthdayForm()
	if form.validate_on_submit():
		record = Record(birthday_name=form.birthday_name.data,
			birthday_date=form.birthday_date.data,author=current_user)
		db.session.add(record)
		db.session.commit()
		flash('Birthday Entry Successful!','success')
		return redirect(url_for('birthdaylist'))
	return render_template('birthdaylist_new.html',title='New Birthday',
		form=form,legend='New Birthday Record')


@app.route("/birthdaylist",methods=['GET'])
@login_required
def birthdaylist():
	records = Record.query.filter_by(author=current_user)
	return render_template('birthdaylist.html',title='Birthday List',records=records)

@app.route("/record/<int:record_id>/update",methods=['GET','POST'])
@login_required
def update_record(record_id):
	record=Record.query.get_or_404(record_id)
	if record.author != current_user:
		abort(403)
	form=BirthdayForm()
	if form.validate_on_submit():
		record.birthday_name=form.birthday_name.data
		record.birthday_date=form.birthday_date.data
		db.session.commit()
		flash("The Birthday record has been updated",'success')
		return redirect(url_for('birthdaylist'))
	elif request.method == 'GET':
		form.birthday_name.data = record.birthday_name
		form.birthday_date.data = record.birthday_date
	return render_template('birthdaylist_new.html',title='Update Birthday',
		form=form,legend='Update Birthday Record')


@app.route("/record/<int:record_id>/delete", methods=['GET','POST'])
@login_required
def delete_record(record_id):
	record=Record.query.get_or_404(record_id)
	if record.author != current_user:
		abort(403)
	db.session.delete(record)
	db.session.commit()
	flash("Birthday Record Deleted!",'success')
	return redirect(url_for('birthdaylist'))

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])
	msg.body = f''' To reset the password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email and enjoy life!
	'''
	mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash("Email has been sent with Instructions to reset your password",'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html',title='Reset Password',form=form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("Invalid / Expired Token",'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()

	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Password Updated! You are now able to login','success')
		return redirect(url_for('login'))

	return render_template('reset_token.html',title='Reset Password',form=form)
