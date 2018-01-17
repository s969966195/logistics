# coding=utf-8
from . import db, login_manager, admin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_admin.contrib.sqla import ModelView


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return "<Role '{}'>".format(self.name)

    @staticmethod
    def insert_roles():
        roles = ['Owner', 'Driver', 'Administrator']
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tables__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(255))
    phonenumber = db.Column(db.String())
    name = db.Column(db.String())
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(id=3).first()
            else:
                self.role = Role.query.filter_by(id=1).first()

    def __repr__(self):
        return "<User '{}'>".format(self.email)

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


class Order(db.Model):
    __tables__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, default=0)
    createtime = db.Column(db.String(64))
    createtimestamp = db.Column(db.Integer)
    starttime = db.Column(db.String(64))
    endtime = db.Column(db.String(64))
    source = db.Column(db.String(64))
    destination = db.Column(db.String(64))
    owner_id = db.Column(db.Integer)
    driver_id = db.Column(db.Integer)

    def __repr__(self):
        return "<Order '{0}, {1}'>".format(self.owner_id, self.id)

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if self.createtime is None:
            self.createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            self.createtimestamp = int(time.time())
        self.status = 0


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
