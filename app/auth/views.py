# coding=utf-8
from . import auth
from .. import db
from ..models import User
from flask import request, redirect, render_template, flash, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = request.form
    if request.method == 'POST':
        if form.get('password') != form.get('password_confirm'):
            flash(u'两次密码输入不一致，请重新输入!')
            return redirect(url_for('auth.register'))
        user = User(email=form.get('email'))
        user.password = form.get('password')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, u'确认您的账户', 'auth/email/confirm', user=user, token=token)
        flash(u"已向您的邮箱发送邮件")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = request.form
    if request.method == 'POST':
        user = User.query.filter_by(email=form.get('email')).first()
        if user is not None and user.verify_password(form.get('password')):
            login_user(user, remember=form.get('remember_me'))
            return redirect(request.args.get('next') or url_for('main.manage'))
        flash(u"用户名或密码错误", 'danger')
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经退出登录', 'warning')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'您已经确认过您的账户, 谢谢!')
    else:
        flash(u'确认链接无效或已过期')
    return redirect(url_for('main.manage'))


@auth.route('/unconfirmed')
def unconfirmed():
    return render_template('auth/unconfirmed.html')


@auth.route('/confirmed')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'确认您的账户', 'auth/email/confirm', user=current_user, token=token)
    flash(u'一封新的确认邮件已经发送到您的邮箱')
    return redirect(url_for('main.manage'))


@auth.route('/edituser/<int:id>', methods=['POST', 'GET'])
@login_required
def edituser(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.phonenumber = request.form.get('phonenumber')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.manage'))
    return render_template('auth/edituser.html', user=user, sidebar=0)


@auth.route('/bedriver')
@login_required
def bedriver():
    user = User.query.filter_by(id=current_user.id).first()
    user.role_id = 2
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.manage'))


reset_data = {}


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    global reset_data
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            reset_token = user.generate_reset_token()
            reset_data = user.get_reset_token(reset_token)
            send_email(user.email, u'重置密码', 'auth/email/reset_password', user=user, token=reset_token, next=request.args.get('next'))
            flash(u'已向您的邮箱发送重置密码邮件')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', temp=0)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    global reset_data
    if not current_user.is_anonymous:
        return redirect(url_for('main.manage'))
    if request.method == 'POST':
        user = User.query.filter_by(id=reset_data['reset']).first()
        if user.reset_password(token, request.form.get('password')):
            flash(u'您的密码已经重置')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.manage'))
    return render_template('auth/reset_password.html', temp=1)
