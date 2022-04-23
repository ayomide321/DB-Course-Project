from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, People, Batting, Pitching, Fielding, Team, AuditTrail
from datetime import datetime


@app.context_processor
def inject_user():
    return dict(ADMIN_NAME=app.config.get('ADMIN_NAME'))


def getTeamName(teamID):
    return Team.query.filter_by(teamID=teamID).first().name

def getPlayerName(playerID):
    firstName = People.query.filter_by(playerID=playerID).first().nameFirst
    lastName = People.query.filter_by(playerID=playerID).first().nameLast
    fullName = firstName + " " + lastName
    return fullName

def getPositionName(positionID):
    positionDic = {'SS' : 'Shortstop',
                    '2B': '2nd Baseman',
                    'OF': 'Outfielder',
                    'C' : 'Catcher',
                    '1B': '1st Baseman',
                    '3B': '3rd Baseman',
                    'P' : 'Pitcher',
                    'LF': 'Left Field',
                    'RF': 'Right Field',
                    'CF': 'Center Field',}
    return positionDic[positionID]

def logAuditTrail(**kwargs):
    if(current_user.is_anonymous):
        return
    playerID = kwargs.get('playerID') or ""
    teamID = kwargs.get('teamID') or ""
    yearID = kwargs.get('yearID') or ""
    actionType = kwargs.get('actionType')
    auditUser = current_user.username

    auditTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if(not playerID and not teamID and not yearID):
        user_action = actionType
    else:
        user_action = "Action: " + actionType + " PlayerID: " + playerID + " TeamID: " + teamID + " YearID: " + yearID
        
    print(user_action)
    currentAudit = AuditTrail(user_action=user_action, time_action=auditTime, username=auditUser)
    db.session.add(currentAudit)
    db.session.commit()

@app.route('/adminpage', methods=['GET', 'POST'])
@login_required
def adminpage():
    username = ""
    if(current_user.is_anonymous):
        logAuditTrail(actionType="Unauthorized access to admin page")
    elif(current_user.username != app.config.get('ADMIN_NAME')):
        logAuditTrail(actionType="Unauthorized access to admin page")
    allTracking = ""
    auditUsers = AuditTrail.query.with_entities(AuditTrail.username).distinct(AuditTrail.username).all()
    if request.method == 'POST':
        username = request.form.get('userID')
        allTracking = AuditTrail.query.filter_by(username=username).all()

    return render_template('admin.html', auditUsers=auditUsers, allTracking=allTracking, username=username)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
def index():
    teamID = ''
    yearID = 0
    allFielding = ''
    currentTeams = Team.query.with_entities(Team.teamID, Team.name).distinct(Team.name).all()
    currentYears = Team.query.with_entities(Team.yearID).distinct(Team.yearID).all()

    if request.method == "POST":
        teamID = request.form.get('teamID')
        yearID = request.form.get('yearID')
        if(yearID):
            int(yearID)
        logAuditTrail(actionType="Search By Team", teamID=teamID, yearID=yearID)
        allFielding = Fielding.query.filter_by(teamID=teamID, yearID=yearID).all()
    else:
        logAuditTrail(actionType="Load Home Page")

    return render_template('team.html', teamPlayers=currentTeams, teamYears = currentYears,
                            allFielding = allFielding, getName = getPlayerName,
                            posName=getPositionName, teamID = teamID,
                            yearIDSet = yearID)


@app.route('/players', defaults={'urlPlayerID': None}, methods=['GET', 'POST'])
@app.route('/players/<urlPlayerID>/')
@login_required
def player(urlPlayerID):
    # babe_ruth = Batting.query.filter_by(playerID="ruthba01").first()
    # print(babe_ruth)
    fName = lName = year = currentPerson = allFielding = auditPlayerID =  ""
    actionType = "Load Player Search Page"

    if(urlPlayerID):
        actionType = "Clicked Player with PlayerID: " + urlPlayerID + " From Home Page"

    currentPerson = People.query.filter_by(playerID=urlPlayerID).first()
    if request.method == "POST":
        fName = request.form.get("fName")
        lName = request.form.get("lName")
        year = request.form.get("year")
        currentPerson = People.query.filter_by(nameFirst=fName, nameLast=lName).first()
        actionType = "Search Player"
        print(currentPerson)
    if(currentPerson):
        auditPlayerID = currentPerson.playerID
        if(year):
            allFielding = Fielding.query.filter_by(yearID=year, playerID=currentPerson.playerID).all()
        else:
            allFielding = Fielding.query.filter_by(playerID=currentPerson.playerID).all()
    logAuditTrail(actionType=actionType, playerID=auditPlayerID, yearID=year)
    return render_template('player.html', title='Home', person=currentPerson, allFielding=allFielding, getTeamName=getTeamName, posName=getPositionName)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username')
            return redirect(url_for('login'))
            logAuditTrail(actionType="User entered invalid username")
        if not user.check_password(form.password.data):
            print(user.check_password(form.password.data))
            print(form.password.data)
            flash('invalid password')
            logAuditTrail(actionType="User entered invalid password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        print(current_user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        
        logAuditTrail(actionType="User has successfully logged in")
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    logAuditTrail(actionType="User has logged out")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        print(user.check_password(form.password.data))
        print(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        logAuditTrail(actionType="User has successfully registered")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

