from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError 

db = SQLAlchemy()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=True)
    user_phonenumber = db.Column(db.String(length=15), nullable=True)
    user_email = db.Column(db.String(length=320), nullable=True, unique=True)
    __table_args__ = (
        db.CheckConstraint(
            'user_phonenumber IS NOT NULL OR user_email IS NOT NULL',
            name='check_phonenumber_and_email'
        ),
    )

class UserForm(FlaskForm):
    user_name = StringField('Name', validators=[Optional(), Length(max=32)])
    user_email = StringField('Email', validators=[Optional(), Email(), Length(max=320)])
    user_phonenumber = StringField('Phone Number', validators=[Optional(), Length(max=11)])
    submit = SubmitField('Submit')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    group_link = db.Column(db.String(32), unique=True, nullable=False)

class GroupForm(FlaskForm):
    group_name = StringField('Group Name', validators=[Optional(), Length(max=32)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Membership(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, primary_key=True)
    # __table_args__ = (
    #     db.UniqueConstraint('user_id', 'group_id', name='unique_membership'),
    # )

class Meetups(db.Model):
    meetup_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    meetup_date = db.Column(db.Date, nullable=False)
    meetup_start_time = db.Column(db.Time, nullable=False)
    meetup_start_time = db.Column(db.Time, nullable=False)

class Freetime(db.Model):
    freetime_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # group_id = db.Column(db.Integer, db.ForeignKey('group.i'), nullable=False)
    freetime_date = db.Column(db.Date, nullable=False)
    freetime_start_time = db.Column(db.Time, nullable=False)
    freetime_end_time = db.Column(db.Time, nullable=False)

class FreetimeForm(FlaskForm):
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    submit = SubmitField('Submit')

class Attendance(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    meetup_id = db.Column(db.Integer, primary_key=True, nullable=False)
    RSVP = db.Column(db.Boolean, nullable=False)