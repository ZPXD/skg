from flask import Flask, render_template, request, redirect, url_for

import flask_wtf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin
from flask_login import login_required, current_user, login_user, logout_user

import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/xd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = ':)'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


# Main

@app.route('/')
def index():
    get_current_github_repo()
    return render_template("index.html")

@app.route('/zajecia/<int:nr>', methods=["GET", "POST"])
def zpxd_meeting_intro(nr):
    meeting_description = get_meeting_info(nr)
    print(meeting_description)
    form = LoginForm()
    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        
        i_want_to_learn = form.i_want_to_learn.data
        week_goal = form.week_goal.data
        q1 = form.q1.data
        q2 = form.q2.data
        q3 = form.q3.data
        homework = form.homework.data

        active_learner = form.active_learner.data
        voice = form.voice.data
        intention = form.intention.data
        return redirect(url_for('zpxd_meeting_main', nr=nr))
    return render_template("intro.html", nr=nr, form=form, meeting_description=meeting_description)

@app.route('/zajecia/<int:nr>/spotkanie', methods=["GET", "POST"])
def zpxd_meeting_main(nr):
    return render_template("spotkanie.html", nr=nr)


# Login

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(password):
                login_user(user, force=True)
                return redirect( url_for('index'))
        else:
            return "user not found"

    return render_template("login.html", form=form)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if User.query.filter_by(email=email).first():
            return 'taki email już istnieje'

        user = User(name=name, email=email, password=password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect( url_for('index'))
    return render_template("signup.html", form=form)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return render_template("logout.html")

@login_required
@app.route('/profile/<name>')
def user(name):
    if name == current_user.name:
        return "ok"
    else:
        return "no"

# Helpers

def get_current_github_repo():
    '''
    to recode
    '''
    url = 'https://github.com/ZPXD/zajecia_programowania_xd'
    where = os.path.join(os.getcwd(), 'data', 'zajecia')
    os.system('git clone {} {}'.format(url, where))


def get_meeting_info(nr):
    '''
    to recode
    '''
    where = os.path.join(os.getcwd(), 'data', 'zajecia')
    if nr in range(1, 12):
        file_path = os.path.join(where, '1_piaskownica', '0'+str(nr), 'README.md')
    elif nr in range(12, 25):
        file_path = os.path.join(where, '2_systematyzacja', '0'+str(nr), 'README.md')
    elif nr in range (25, 40):
        file_path = os.path.join(where, '3_tbd', '0'+str(nr), 'README.md')

    readme = open(file_path).readlines()
    meeting_description = []
    for i, line in enumerate(readme):
        if i == 0:
            headline = line
        if i in [3,4,5]:
            meeting_description.append(line)
    meeting_description = ' '.join(meeting_description)
    return meeting_description


# DB Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def set_password(self,password):
        self.password = generate_password_hash(password)
     
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Meeting(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nr = db.Column(db.String(120))

    i_want_to_learn = db.Column(db.String(120))
    week_goal = db.Column(db.String(120))

    q1 = db.Column(db.String(120))
    q2 = db.Column(db.String(120))
    q3 = db.Column(db.String(120))
    homework = db.Column(db.String(120))

    active_learner = db.Column(db.String(120))
    voice = db.Column(db.String(120))

    intention = db.Column(db.String(120))


@app.before_first_request
def create_all():
    db.create_all()
    #get_current_github_repo() # if h=n


# Forms

class MeetingForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = StringField(validators=[DataRequired()])

    i_want_to_learn = StringField(validators=[DataRequired()])
    week_goal = StringField(validators=[DataRequired()])

    q1 = StringField(validators=[DataRequired()])
    q2 = StringField(validators=[DataRequired()])
    q3 = StringField(validators=[DataRequired()])
    homework = StringField(validators=[DataRequired()])

    choices_active_learner = [
        ('Tak', 'Tak'),
        ('Dzisiaj głównie słucham i robię ćwiczenia', 'Dzisiaj głównie słucham i robię ćwiczenia'),
        ('Jestem z doskoku, jadę na rowerze :)', 'Jestem z doskoku, jadę na rowerze :)'),
        ('Oglądam po czasie', 'Oglądam po czasie'),
    ]

    choices_voice = [
        ('Mam ogarnięty mikrofon i dźwięk', 'Mam ogarnięty mikrofon i dźwięk'),
        ('Chyba tak', 'Chyba tak'),
        ('Dzisiaj jeszcze nie mam', 'Dzisiaj jeszcze nie mam'),
    ]
    active_learner = StringField(choices=choices_active_learner)
    voice = StringField(choices=choices_voice)

    intention = StringField(validators=[DataRequired()])

    button = SubmitField('zaloguj się')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = StringField('hasło', validators=[DataRequired()])
    submit = SubmitField('zaloguj się')


class SignupForm(FlaskForm):
    name = StringField('nazwa użytkownika', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = StringField('hasło', validators=[DataRequired()])
    confirm_password = StringField('powtórz hasło', validators=[DataRequired()])
    submit = SubmitField('załóż konto')


# Errors

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html'), 500


if __name__=="__main__":
    app.run(debug=True)
