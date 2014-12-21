from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, abort, make_response, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    return render_template('index.html',title='Home',user=user)

@app.route('/chores')
def home():
    user = g.user
    return render_template('chores.html', title='Chores',user=user)

#start api test
chores = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Clean Bathroom',
        'description': u'Need to clean toilet and bathtub.',
        'done': False
    }
]

@app.route('/todo/api/v1.0/chores', methods=['GET'])
def get_chores():
    return jsonify({'chores': map(make_public_chore, chores)})

@app.route('/todo/api/v1.0/chores/<int:chore_id>', methods=['GET'])
def get_chore(chore_id):
    chore = filter(lambda t: t['id'] == chore_id, chores)
    if len(chore) == 0:
        abort(404)
    return jsonify({'chore':chore[0]})

@app.route('/todo/api/v1.0/chores', methods=['POST'])
def create_chore():
    if not request.json or not 'title' in request.json:
        abort(400)
    chore = {
            'id': chores[-1]['id'] + 1,
            'title': request.json['title'],
            'description': request.json.get('description', ""),
            'done': False
        }
    chores.append(chore)
    return jsonify({'chore': chore}), 201

@app.route('/todo/api/v1.0/chores/<int:chore_id>', methods=['PUT'])
def update_chore(chore_id):
    chore = filter(lambda t: t['id'] == chore_id, chores)
    if len(chore) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    chore[0]['title'] = request.json.get('title', chore[0]['title'])
    chore[0]['description'] = request.json.get('description', chore[0]['description'])
    chore[0]['done'] = request.json.get('done', chore[0]['done'])
    return jsonify({'chore': chore[0]})

@app.route('/todo/api/v1.0/chores/<int:chore_id>', methods=['DELETE'])
def delete_chore(chore_id):
    chore = filter(lambda t: t['id'] == chore_id, chores)
    if len(chore) == 0:
        abort(404)
    chores.remove(chore[0])
    return jsonify({'result': True})

def make_public_chore(chore):
    new_chore = {}
    for field in chore:
        if field == 'id':
            new_chore['uri'] = url_for('get_chore', chore_id=chore['id'], _external=True)
        else:
            new_chore[field] = chore[field]
    return new_chore

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#end api test

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #login and validate the user
        session['remember_me'] = form.remember_me.data
        flash("Logged in successfully.")
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(username=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/settings')
@login_required
def settings():
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
