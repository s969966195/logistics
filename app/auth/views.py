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
def logout():
    logout_user()
    flash(u'您已经退出登录', 'warning')
    return redirect(url_for('main.manage'))


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
