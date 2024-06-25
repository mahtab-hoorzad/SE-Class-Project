from flask import Flask, render_template, request, redirect, url_for,flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user  
from datetime import datetime, timedelta
import uuid
from email_validator import validate_email, EmailNotValidError
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rendezvous.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'RVAendezouspp'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, UserForm, Group, GroupForm, Freetime, FreetimeForm 

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_name = form.user_name.data
        user_email = form.user_email.data
        user_phonenumber = form.user_phonenumber.data
        if user_email:
            user = User.query.filter_by(user_email=user_email).first()
        elif user_phonenumber:
            user = User.query.filter_by(user_phonenumber=user_phonenumber).first()
        else:
            flash('Please enter either an email or a phone number', 'danger')
            return render_template('login.html', form=form)
        print(f"User Name: {user_name}, Email: {user_email}, Phone Number: {user_phonenumber}") 
        if user:
            login_user(user, remember=True)
            session.permanent = True
            flash('You Logged in Successfully!', 'success')
            return redirect(url_for('create_group'))
        else:
            if user_email:
                new_user = User(user_name=user_name, user_email=user_email)
            else:
                new_user = User(user_name=user_name, user_phonenumber=user_phonenumber)
        db.session.add(new_user)
        try:
            db.session.commit()
            login_user(new_user, remember=True)
            session.permanent = True
            flash('You Logged in Successfully!', 'success')
            return redirect(url_for('create_group'))
        except Exception as e:
            db.session.rollback()
            flash('Error: ' + str(e), 'danger')
        return redirect(url_for('create_group'))
    
    return render_template('login.html', form=form)

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    if request.method == 'POST':
        print("Form submitted")
        print(request.form) 
        if form.validate_on_submit():
            print("Form validated") 
            group_name = form.group_name.data
            start_date = form.start_date.data
            end_date = form.end_date.data
            unique_id = uuid.uuid4().hex
            #base_url = request.host_url
            #group_link = f"{base_url}{unique_id}"
            group_link = unique_id
            print(f"name: {group_name}, sdate: {start_date}, edate: {end_date}, link: {group_link}")
            new_group = Group(group_name=group_name, start_date=start_date, end_date=end_date, group_link=group_link)
            db.session.add(new_group)
            try:
                db.session.commit()
                flash('Group Created Successfully!', 'success')
                return redirect(url_for('group_details', group_link=unique_id))
            except Exception as e:
                db.session.rollback()
                flash('Error: ' + str(e), 'danger')
        else:
            print("Form not validated")  
            print(form.errors)  
            flash('Form validation failed', 'danger')
    return render_template('create_group.html', form=form)

@app.route('/group_details/<group_link>', methods=['GET', 'POST'])
@login_required
def group_details(group_link):
    group_link = session.get('group_link')
    group = Group.query.filter_by(group_link=group_link).first_or_404()
    form = FreetimeForm()
    if request.method == 'POST' and form.validate_on_submit():
        user_id = current_user.user_id 
        selected_availability = request.form.getlist('availability')
        for item in selected_availability:
            date, time = item.split()
            start_time = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
            end_time = start_time + timedelta(hours=1)
            new_availability = Freetime(user_id=current_user.id, freetime_date=start_time.date(),
                                        freetime_start_time=start_time.time(), freetime_end_time=end_time.time())
            db.session.add(new_availability)
        try:
            db.session.commit()
            flash('Availability Submitted Successfully!', 'success')
            return redirect(url_for('group_details.html'))
        except Exception as e:
            db.session.rollback()
            flash('Error: ' + str(e), 'danger')

        start_date = Group.start_date.date()
        end_date = Group.end_date.date()
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
        hours = [f"{i}:00" for i in range(24)]  

    return render_template('group_details.html', group=group,form=form,user_=user_id)

# @app.route('/availability', methods=['POST'])
# def submit_availability():
#     data = request.json
#     group_id = data['group_id']
#     selected_times = data['selected_times']
#     for time in selected_times:
#         new_availability = Availability(group_id=group_id, day=time['day'], hour=time['hour'])
#         db.session.add(new_availability)
#     db.session.commit()
#     return jsonify({"message": "Availability submitted successfully"}), 200

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
