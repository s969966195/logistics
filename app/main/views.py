# coding=utf-8
from flask import render_template, request, redirect, url_for, current_app, make_response
from . import main
from .. import db
from ..models import Order, User
from flask_login import login_required, current_user
import time


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/manage')
@login_required
def manage():
    return render_template('manage.html', sidebar=1)


@main.route('/createorder', methods=['GET', 'POST'])
@login_required
def createorder():
    form = request.form
    if request.method == 'POST':
        order = Order(owner_id=current_user.id)
        order.source = form.get('source')
        order.destination = form.get('destination')
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('main.showorder'))
    return render_template('order/createorder.html', sidebar=2)


@main.route('/searchorder', methods=['GET', 'POST'])
@login_required
def searchorder():
    etime = time.strftime('%Y-%m-%dT%H:%M', time.localtime(time.time()))
    stime = time.strftime('%Y-%m-%dT%H:%M', time.localtime(time.time()-86400))
    if request.method == 'POST':
        stime = request.form.get('stime')
        sttime = int(time.mktime(time.strptime(stime.replace('T', ' ') + ':00', "%Y-%m-%d %H:%M:%S")))
        etime = request.form.get('etime')
        ettime = int(time.mktime(time.strptime(etime.replace('T', ' ') + ':00', "%Y-%m-%d %H:%M:%S")))
        page = request.args.get('page', 1, type=int)
        pagination = db.session.query(Order).filter(Order.createtimestamp.between(sttime, ettime)).order_by(Order.createtime.desc()).paginate(page, per_page=current_app.config['FLASKY_ORDERS_PER_PAGE'], error_out=False)
        orders = pagination.items
        return render_template('order/searchorder.html', sidebar=3, stime=stime, etime=etime, temp=1, orders=orders, pagination=pagination, User=User)
    return render_template('order/searchorder.html', sidebar=3, stime=stime, etime=etime, temp=0)


@main.route('/showorder')
@login_required
def showorder():
    orderstatus = request.cookies.get('orderstatus', '')
    if not orderstatus:
        query = Order.query.filter_by(owner_id=current_user.id)
    else:
        orderstatus = int(orderstatus)
        if current_user.role_id == 2:
            if orderstatus == 0:
                query = Order.query.filter_by(status=orderstatus)
            elif orderstatus == 1:
                query = Order.query.filter_by(status=orderstatus, driver_id=current_user.id)
        else:
            query = Order.query.filter_by(owner_id=current_user.id, status=orderstatus)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Order.createtime.desc()).paginate(page, per_page=current_app.config['FLASKY_ORDERS_PER_PAGE'], error_out=False)
    orders = pagination.items
    return render_template('order/showorder.html', sidebar=4, orders=orders, User=User, orderstatus=orderstatus, pagination=pagination)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.showorder')))
    resp.set_cookie('orderstatus', '', max_age=30*24*60*60)
    return resp


@main.route('/unanswered')
@login_required
def show_unanswered():
    resp = make_response(redirect(url_for('.showorder')))
    resp.set_cookie('orderstatus', '0', max_age=30*24*60*60)
    return resp


@main.route('/unfinished')
@login_required
def show_unfinished():
    resp = make_response(redirect(url_for('.showorder')))
    resp.set_cookie('orderstatus', '1', max_age=30*24*60*60)
    return resp


@main.route('/finished')
@login_required
def show_finished():
    resp = make_response(redirect(url_for('.showorder')))
    resp.set_cookie('orderstatus', '2', max_age=30*24*60*60)
    return resp


@main.route('/answer/<int:orderid>')
@login_required
def answer(orderid):
    order = Order.query.filter_by(id=orderid).first()
    order.status = 1
    order.starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    order.driver_id = current_user.id
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('.showorder'))


@main.route('/finish/<int:orderid>')
@login_required
def finish(orderid):
    order = Order.query.filter_by(id=orderid).first()
    order.status = 2
    order.endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('.showorder'))
