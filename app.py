from flask import Flask, render_template, request, redirect, url_for,flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user  
from datetime import datetime, timedelta
import uuid
from email_validator import validate_email, EmailNotValidError
from models import db
from urllib.parse import urlparse, urljoin
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rendezvous.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'RVAendezouspp'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, UserForm, Group, GroupForm, Freetime, FreetimeForm ,Membership

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if request.method == 'POST':
        print("Form submitted")
        if form.validate_on_submit():
            user_name = form.user_name.data
            user_email = form.user_email.data
            # the next does not work
            next_page = request.args.get('next') 

            user=None
            if user_email:
                user = User.query.filter_by(user_email=user_email).first()
            else:
                flash('Please enter an email', 'danger')
                return render_template('login.html', form=form)

            print(f"User Name: {user_name}, Email: {user_email}")

            if user:
                login_user(user, remember=True)
                session.permanent = True
                flash('You Logged in Successfully!', 'success')
            else:
                new_user = User(user_name=user_name, user_email=user_email)
                db.session.add(new_user)
                try:
                    db.session.commit()
                    login_user(new_user, remember=True)
                    session.permanent = True
                    flash('You Logged in Successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error: ' + str(e), 'danger')

            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('create_group'))
        else:
                print(form.errors)
                flash('Form validation failed', 'danger')

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
            base_url = request.host_url
            group_link = unique_id
            print(f"name: {group_name}, sdate: {start_date}, edate: {end_date}, link: {group_link}")
            new_group = Group(group_name=group_name, start_date=start_date, end_date=end_date, group_link=group_link)
            db.session.add(new_group)
            try:
                db.session.commit()
                new_membership = Membership(user_id=current_user.id, group_id=new_group.id)
                db.session.add(new_membership)
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
    group = Group.query.filter_by(group_link=group_link).first_or_404()

    start_date = group.start_date.date() if isinstance(group.start_date, datetime) else group.start_date
    end_date = group.end_date.date() if isinstance(group.end_date, datetime) else group.end_date
    
    dates =[]
    current_date = start_date
    while current_date <= end_date :
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    hours = [f"{i}:00" for i in range(24)]  
    
    user_id = session.get('_user_id')

    membership = Membership.query.filter_by(user_id=user_id, group_id=group.id).first()
    if not membership:
        new_membership = Membership(user_id=user_id, group_id=group.id)
        db.session.add(new_membership)
        try:
            db.session.commit()
            flash('You have been added to the group.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    form = FreetimeForm()
    if request.method == 'POST': 
        print("Form submited")
        print(f"fd:{form.data}")
        print (f"ui:{current_user.id}, gi:{group.id}, list:{request.form.getlist('availability')}")
        if form.validate_on_submit():
            selected_availability = request.form.getlist('availability')
            if selected_availability:
                for item in selected_availability:
                    date, time = item.split()
                    start_time = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
                    end_time = (start_time + timedelta(hours=1)).time()
                    new_availability = Freetime(user_id=current_user.id,group_id=group.id, freetime_date=start_time.date(),
                                                freetime_start=start_time.time(), freetime_end=end_time)
                    db.session.add(new_availability)
            try:
                db.session.commit()
                flash('Availability Submitted Successfully!', 'success')
                return redirect(url_for('availability',group_id=group.id))
            except Exception as e:
                db.session.rollback()
                flash('Error: ' + str(e), 'danger')
        else: 
            print("not validated")
    return render_template('group_details.html', group=group,form=form,user_id=user_id,dates=dates,hours=hours,membership=membership)

def find_common_availability(freetimes):
    time_slots = defaultdict(int)
    for freetime in freetimes:
        current_time = datetime.combine(freetime.freetime_date, freetime.freetime_start)
        end_time = datetime.combine(freetime.freetime_date, freetime.freetime_end)
        while current_time < end_time:
            time_slots[current_time] += 1
            current_time += timedelta(hours=1)

    num_users = len(set(freetime.user_id for freetime in freetimes))
    common_slots = [dt for dt, count in time_slots.items() if count == num_users]
    
    return [dt.strftime('%Y-%m-%d %H:%M') for dt in common_slots]

@app.route('/availability/<int:group_id>', methods=['GET','POST'])
def availability(group_id):
    group = Group.query.get_or_404(group_id)
    freetimes = Freetime.query.filter_by(group_id=group_id).all()
    common_slots = find_common_availability(freetimes)
    dates = [(group.start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((group.end_date - group.start_date).days + 1)]
    hours = [f"{i}:00" for i in range(24)]
    print("Common Slots:", common_slots)
    print("Dates:", dates)
    print("Hours:", hours)
    return render_template('availability.html', group=group,common_slots=common_slots ,dates=dates ,hours=hours)
                           
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
    