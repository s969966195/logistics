# coding=utf-8
from flask import render_template, request
from . import main
from flask_login import login_required, current_user


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/manage')
@login_required
def manage():
    return render_template('manage.html')
