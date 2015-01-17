from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify, abort, make_response, request, json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.httpauth import HTTPBasicAuth
from app import app, db, lm
from .forms import LoginForm, CreateForm, ResetForm, HouseForm
from .models import User, Chore, House
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
    return render_template('index.html',title='index',user=user)

@app.route('/home')
@login_required
def home():
    user = g.user
    return render_template('home.html', title='Home', user=user)

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
        return render_template('home.html', title='Home', user=user)
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
        #if not username:
            #flash("Please enter a username")
        #if not password:
            #flash("Please enter a password")
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
    #pdb.set_trace()
    logout_user()
    return redirect(url_for('index'))

@app.route('/chores')
@login_required
def chores():
    user = g.user
    return render_template('chores.html',title='Chores',user=user)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    chores = [
            {'author': user, 'title': 'Buy milk'},
            {'author': user, 'title': 'Get kisses from Kevin'}
            ]
    return render_template('user.html',
                            user=user,
                            chores=chores)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.username)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flask('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flask('You can\'t follow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flask('Cannot follow ' + username + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('user', username=username))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

#start api test
auth = HTTPBasicAuth()

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
        else:
            new_task[field] = task[field]
    return new_task

@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
@auth.login_required
def get_tasks():
    return jsonify( { 'tasks': map(make_public_task, tasks) } )

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
@auth.login_required
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    return jsonify( { 'task': make_public_task(task[0]) } )

@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify( { 'task': make_public_task(task) } ), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['PUT'])
@auth.login_required
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify( { 'task': make_public_task(task[0]) } )

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
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

@app.route('/api/v1.0/login')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/v1.0/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' %g.user.username })

#end api test



