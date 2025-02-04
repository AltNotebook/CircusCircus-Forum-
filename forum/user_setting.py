import os
import secrets
from flask import *
from flask_login.utils import login_required
from forum.app import app
from flask_sqlalchemy import SQLAlchemy
#from forum.model import User
from forum.model import *
from forum.forum import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


db = SQLAlchemy(app)

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext =os.path.splitext(form_picture.filename)
    picture_fn= random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@login_required
@app.route('/action_profile', methods=['GET','POST'])
def action_profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your profile has been updated!','Success')
        return redirect(url_for('action_profile'))
    elif request.method == 'GET' :
        form.username.data= current_user.username
        form.email.data=current_user.email

    image_file=url_for('static',filename='/' + str(current_user.image_file))  # this is current user image from location
    return render_template('account.html' ,image_file=image_file,form=form) #assigning image_file to account.html


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
