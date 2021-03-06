from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify, abort, make_response, request, json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.httpauth import HTTPBasicAuth
from app import app, db, lm
from .forms import LoginForm, CreateForm, ResetForm, HouseForm, MessageForm
from .models import User, Chore, House, Message, Event
import datetime
from config import MESSAGES_PER_PAGE, CHORES_PER_PAGE
import pdb

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
def index():
    user = g.user
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    return render_template('index.html',title='index', user=user)

@app.route('/home', methods=['GET', 'POST'])
@app.route('/home/<int:page>', methods=['GET', 'POST'])
@login_required
def home(page=1, chore_page=1):
    user = g.user
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(message=form.message.data, timestamp=datetime.datetime.utcnow(), sender=user, home=user.home, receiver=None)
        db.session.add(message)
        db.session.commit()
        flash('Your message is sent!')
        return redirect(url_for('home'))
    house_messages = user.house_messages().paginate(page, MESSAGES_PER_PAGE, False)
    messages = user.messages.paginate(page, MESSAGES_PER_PAGE, False)
    chores = user.sorted_chores().paginate(chore_page, CHORES_PER_PAGE, False)
    return render_template('home.html',
                            title='Home',
                            user=user,
                            form=form,
                            house_messages=house_messages,
                            messages=messages,
                            chores=chores)

@app.route('/forgot_password')
def forgot_password():
    form = ResetForm()
    if form.validate_on_submit():
        # reset password after email confirmation
        return redirect(url_for('register'))
    return render_template('forgot_password.html', title='Forgot Password', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form = CreateForm()
    if form.validate_on_submit():
        render = False
        # create new account for user...
        username = form.username.data.lower()
        email = form.email.data
        password = form.password.data
        repeat_password = form.repeat_password.data
        if username is None or password is None or email is None or repeat_password is None:
            flash('Missing Fields. Please resubmit with all fields completed.')
            render = True
            abort(400) # missing arguments
        if User.query.filter_by(username=username).first() is not None:
            flash('Preexisting user. Please choose a different username')
            render = True
            #abort(400) # existing user
        if password != repeat_password:
            flash('Passwords do not match.')
            render = True
            #abort(400)
        if render:
            return render_template('register.html', title='New Account', form=form)
        user = User(username=username, email=email)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        g.user = user
        login_user(g.user, remember=False)
        return redirect(url_for("join_house"))
    return render_template('register.html', title='New Account', form=form)

@app.route('/join_house', methods=['GET', 'POST'])
@login_required
def join_house():
    if g.user is None:
        return redirect(url_for('register'))
    form = HouseForm()
    if form.validate_on_submit():
        render = False
        housename = form.housename.data.lower()
        house_password = form.password.data
        repeat_password = form.password.data
        if  housename is None or house_password is None or repeat_password is None:
            flash('Missing Fields.Please resubmit with all fields completed.')
            render = True
            #abort(400) # missing arguments
        if house_password != repeat_password:
            flash('Passwords do not match.')
            render = True
            #abort(400)
        if House.query.filter_by(housename=housename).first() is not None:
            # Join a preexisting House
            house = House.query.filter_by(housename=housename).first()
            if not house.verify_password(password=house_password):
                flash('Invalid password.')
                render = True
        else:
            house = House(housename=housename)
            house.hash_password(house_password)
            db.session.add(house)
            db.session.commit()
        if render:
            return render_template('join_house.html', title='Join/Create a House', form=form)
        user = g.user
        g.user.home = house
        db.session.add(g.user)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('join_house.html', title='Join/Create a House', form=form)

@app.route('/blank')
@login_required
def blank():
    user = g.user
    return render_template('blank.html', title='Home', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        session['remember_me'] = form.remember_me.data
        username = form.username.data.lower()
        password = form.password.data
        result = verify_password(username, password)
        if result:
            login_user(g.user, remember=session['remember_me'])
            return redirect(request.args.get("next") or url_for("home"))
        else:
            flash("Incorrect Login")
            return render_template('login.html', title='Sign In', form=form)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/settings')
@login_required
def settings():
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chores', methods=['GET', 'POST'])
@app.route('/chores/<int:page>', methods=['GET', 'POST'])
@login_required
def chores(page=1):
    user = g.user
    #return render_template('chores.html',title='Chores',user=user)
    messages = user.messages.paginate(page, MESSAGES_PER_PAGE, False)
    chores = user.sorted_chores().paginate(page, CHORES_PER_PAGE, False)
    return render_template('chores.html',
                            title='Chores',
                            user=user,
                            messages=messages,
                            chores=chores)


@app.route('/personal_chores', methods=['GET', 'POST'])
@app.route('/personal_chores/<int:page>', methods=['GET', 'POST'])
@login_required
def personal_chores(page=1):
    user = g.user
    #return render_template('chores.html',title='Chores',user=user)
    messages = user.messages.paginate(page, MESSAGES_PER_PAGE, False)
    chores = user.sorted_chores().paginate(page, CHORES_PER_PAGE, False)
    return render_template('chores.html',
                            title='Chores',
                            user=user,
                            messages=messages,
                            chores=chores)


@app.route('/calendar', methods=['GET', 'POST'])
@app.route('/calendar/<int:page>', methods=['GET', 'POST'])
@login_required
def calendar(page=1):
    user = g.user
    messages = user.house_messages().paginate(page, MESSAGES_PER_PAGE, False)
    return render_template('calendar.html',
                            title='Chores',
                            user=user,
                            messages=messages)

@app.route('/user/<username>')
@app.route('/user/<int:page>', methods=['GET', 'POST'])
@login_required
def user(username, page=1):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    messages = user.messages.paginate(page, MESSAGES_PER_PAGE, False)
    chores = user.sorted_chores().paginate(page, CHORES_PER_PAGE, False)
    return render_template('user.html',
                            title='Profile',
                            user=user,
                            messages=messages,
                            chores=chores)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.username)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

"""

API Section below

"""
#start api test
auth = HTTPBasicAuth()

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify( { 'error': 'Bad request', 'message': error} ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/api/v1.0/login')
def get_auth_token():
    username = request.args.get('username')
    password = request.args.get('password')
    print "HERE"
    if not verify_password(username, password):
        return make_response(jsonify({'error': 'Bad request', 'message': 'username and password not accepted.', 'code': 'invalid_username_password'}), 400)
    user = User.query.filter_by(username=username).first()
    g.user = user
    token = g.user.generate_auth_token(600)
    return make_response(jsonify({'token': token.decode('ascii'), 'duration': 600}), 200)


@app.route('/api/v1.0/logout')
@auth.login_required
def remove_auth_token(user):
    user.invalidate_auth_token()
    return make_response(jsonify( { 'status': '200' } ), 200)


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
        else:
            new_task[field] = task[field]
    return new_task

@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
@login_required
def get_tasks():
    user = g.user
    tasks = user.get_chores()
    return jsonify( { 'tasks': tasks } )

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
@login_required
def get_task(chore_id):
    user = g.user
    chore = Chore.query.get(chore_id)
    chore = user.get_chore(chore)
    if len(chore) == 0:
        abort(404)
    return jsonify( { 'task': chore } )

@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
@login_required
def create_task():
    user = g.user
    if not request.json or not 'title' in request.json:
        abort(400)
    chore = Chore(title=request.json['title'], description=request.json.get('description', ""), status=False, timestamp=datetime.datetime.utcnow(), author=user, home=user.home)
    db.session.add(chore)
    db.session.commit()
    return jsonify( { 'task': user.get_chore(chore) } ), 201

@app.route('/todo/api/v1.0/tasks/<int:chore_id>', methods = ['PUT'])
@login_required
def update_chore(chore_id):
    user = g.user
    chore = Chore.query.get(chore_id)
    chore_dict = user.get_chore(chore)
    if len(chore_dict) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json or 'description' in request.json or type(request.json['done']) is not bool:
        if 'title' in request.json and type(request.json['title']) != unicode:
            abort(400)
        if 'description' in request.json and type(request.json['description']) is not unicode:
            abort(400)
        if 'done' in request.json and type(request.json['done']) is not bool:
            abort(400)
        chore.title = request.json.get('title')
        chore.description = request.json.get('decription')
        chore.status = request.json.get('done')
    else:
        chore.status = request.json.get('done')
    db.session.add(chore)
    db.session.commit()
    return jsonify( { 'task': user.get_chore(chore) }), 200

@app.route('/todo/api/v1.0/tasks/<int:chore_id>', methods = ['DELETE'])
@login_required
def delete_task(chore_id):
    chore = Chore.query.get(chore_id)
    db.session.delete(chore)
    db.session.commit()
    return jsonify( { 'result': True } )

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/v1.0/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None or email is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/v1.0/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/v1.0/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' %g.user.username })

#end api test

@app.route('/api/v1.0/message_box', methods=['GET'])
def message_box():
    print "message!"
    return jsonify({ 'data': 'Hello, %s!' %g.user.username })

@app.route('/api/v1.0/get_img', methods=['GET'])
def get_random_img():
    print "here!"

