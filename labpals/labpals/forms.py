from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileRequired, FileAllowed
from labpals.models import User, Group
from flask import request
from labpals import app


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class UserRegistrationForm(FlaskForm):
    groupaffiliation= StringField('Group Affiliation')
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    extensions = app.config['ALLOWED_EXTENSIONS']
    file = FileField('Upload File', validators=[FileRequired(), FileAllowed(extensions,
                                                                            "The file extension isn't supported "
                                                                            "currently. Allowed extensions include "
                                                                            + str(extensions))])
    submit = SubmitField('Upload')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class GroupRegistrationForm(FlaskForm):
    groupname = StringField('Group Name', validators=[DataRequired()])
    researchcenter = StringField('Affiliated Research Center (University, etc.)', validators=[DataRequired()])
    researchfield = StringField('Field of Research', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    website = StringField('Website')
    submit = SubmitField('Register')

    def validate_groupname(self, groupname):
        name = Group.query.filter_by(groupname=groupname.data).first()
        if name is not None:
            raise ValidationError('Please use a different group name.')

    def validate_email(self, email):
        groupmail = Group.query.filter_by(email=email.data).first()
        if groupmail is not None:
            raise ValidationError('Please use a different email address.')
