from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify, abort, make_response, request, json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.httpauth import HTTPBasicAuth
from app import app, db, lm, client, views
from .forms import LoginForm, CreateForm, ResetForm, HouseForm, MessageForm
from .models import User, Chore, House, Message, Event
import datetime
from config import MESSAGES_PER_PAGE, CHORES_PER_PAGE, TWILIO_NUMBER
import pdb

import twilio

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/twilio/send_message')
@login_required
def send_message():
    user = g.user
    try:
        message = client.messages.create(
                body="Radhika I love you <3",
                to="+17608213933",
                from_=TWILIO_NUMBER
    )
    except twilio.TwilioRestException as e:
        print e
