# -*- coding: UTF-8 -*-
import os
from flask import Flask, g, render_template, request, jsonify, url_for, send_file, redirect
from models import db_session, Sponsor, Event, EventInfo, Participant, User, UserEvent
import settings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid
from datetime import datetime
from sqlalchemy.sql import func  # Importing func

app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = str(uuid.uuid4())
manager = LoginManager(app)

@app.route("/")
def index():
    return redirect(url_for('MainPage'))

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('MainPage', page_name='index'))
        else:
            return render_template('login.htm', error='Invalid username or password')
    return render_template("login.html")

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('MainPage', page_name='index'))

@app.route("/registration/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        new_user = User(name=username, password=password, mail=email)
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)
        return redirect(url_for('MainPage'))
    return render_template("registration.htm")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.htm'), 404

@app.route("/Main/")
def MainPage():
    events_ = db_session.query(Event).all()
    return render_template("Main.htm", page_name="Main", events=events_)

@app.route("/Participants/")
def ParticipantsPage():
    partic = db_session.query(Participant).all()
    return render_template("Participants.htm", page_name="Участники", participants=partic)

@app.route("/Sponsors/")
def SponsorsPage():
    sponsors = db_session.query(Sponsor).all()
    return render_template("Sponsors.htm", page_name="Спонсоры", sponsors=sponsors)

@app.route("/ContactInformation/")
def ContactInformationPage():
    info = db_session.query(EventInfo).all()
    return render_template("ContactInformation.htm", page_name="Контакты", information=info)

@app.route("/Schedule/")
def SchedulePage():
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        info = db_session.query(Event).filter(func.date(Event.date_time) == date.date()).all()
    else:
        info = db_session.query(Event).all()
    return render_template("Schedule.htm", page_name="Расписание", information=info)

@app.route("/register_for_event/<int:event_id>/", methods=['POST'])
@login_required
def register_for_event(event_id):
    existing_registration = db_session.query(UserEvent).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not existing_registration:
        new_registration = UserEvent(user_id=current_user.id, event_id=event_id)
        db_session.add(new_registration)
        db_session.commit()
    return redirect(url_for('EventById', id=event_id))


@app.route("/MyEvents/remove/<int:event_id>", methods=['POST'])
@login_required
def RemoveEventFromMyEvents(event_id):
    user_event = db_session.query(UserEvent).filter_by(user_id=current_user.id, event_id=event_id).first()
    if user_event:
        db_session.delete(user_event)
        db_session.commit()
    return redirect(url_for('MyEventsPage'))

@app.route("/MyEvents/")
@login_required
def MyEventsPage():
    my_events = db_session.query(Event).join(UserEvent).filter(UserEvent.user_id == current_user.id).all()
    return render_template("MyEvents.htm", page_name="Мои мероприятия", events=my_events)


@app.route("/Sponsors/SponsorsCard/<int:id>/")
def SponsorById(id):
    card = db_session.query(Sponsor).filter(Sponsor.id == id).first()
    return render_template("SponsorsCard.htm", page_name='Спонсор', card=card)

@app.route("/Main/card/<int:id>/")
def EventById(id):
    event = db_session.query(Event).filter(Event.id == id).first()
    return render_template("card.htm", page_name='Мероприятие', event_=event)

@app.route("/<page_name>/")
def main(page_name):
    return render_template(page_name + ".htm")

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5057, debug=True)
