# -*- coding: utf-8 -*-

from AtelierApp import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from unidecode import unidecode
from sqlalchemy_utils import aggregated

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=False, unique=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(16))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    @lm.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
    
    @property
    def is_admin(self):
        adminRole = Role.query.filter_by(name='Admin').first()
        return self.role==adminRole

    @staticmethod
    def registerAdmin(email, username, password):
        user = User(email=email, username=username)
        user.password = password
        adminRole = Role.query.filter_by(name='Admin').first()
        user.role = adminRole
        db.session.add(user)
        db.session.commit()
        return user


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.ATTEND, True),
            'Admin': (0xff, False)
            }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
                db.session.commit()

class Permission:
    ATTEND = 0x01
    ORDER = 0x02
    COMMENT = 0x04
    ADMINISTER = 0x80


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True, nullable=False)
    filepath = db.Column(db.String(256))
    slideshow = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'))

    def __repr__(self):
        return '<Photo %r>' % (self.filename)


class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=False, unique=True)
    photos = db.relationship('Photo', backref='collection', lazy='dynamic')

    def __repr__(self):
        return '<Collection %r>' % (self.name)

    @staticmethod
    def register(fullname):
        collection = Collection(fullname=unicode(fullname, 'utf-8'), name = Collection.make_unique_name(fullname))
        db.session.add(collection)
        db.session.commit()
        return collection

    @staticmethod
    def make_unique_name(fullname):
        decoded = unidecode(unicode(fullname, 'utf-8'))
        decoded = '-'.join(decoded.split())
        decoded = decoded.lower()
        if Collection.query.filter_by(name=decoded).first() is None:
            return decoded
        version = 2
        while True:
            new_name = decoded + str(version)
            if Collection.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        return new_name
    

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=False, unique=True)
    photos = db.relationship('Photo', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % (self.name)

    @staticmethod
    def register(fullname):
        collection = Category(fullname=unicode(fullname, 'utf-8'), name = Category.make_unique_name(fullname))
        db.session.add(collection)
        db.session.commit()
        return collection

    @staticmethod
    def make_unique_name(fullname):
        decoded = unidecode(unicode(fullname, 'utf-8'))
        decoded = '-'.join(decoded.split())
        decoded = decoded.lower()
        if Category.query.filter_by(name=decoded).first() is None:
            return decoded
        version = 2
        while True:
            new_name = decoded + str(version)
            if Category.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        return new_name


class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=False, unique=True)
    photos = db.relationship('Photo', backref='subcategory', lazy='dynamic')

    def __repr__(self):
        return '<Subcategory %r>' % (self.name)

    @staticmethod
    def register(fullname):
        collection = Subcategory(fullname=unicode(fullname, 'utf-8'), name = Subcategory.make_unique_name(fullname))
        db.session.add(collection)
        db.session.commit()
        return collection

    @staticmethod
    def make_unique_name(fullname):
        decoded = unidecode(unicode(fullname, 'utf-8'))
        decoded = '-'.join(decoded.split())
        decoded = decoded.lower()
        if Subcategory.query.filter_by(name=decoded).first() is None:
            return decoded
        version = 2
        while True:
            new_name = decoded + str(version)
            if Subcategory.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        return new_name

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(256))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    capacity = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    customers = db.relationship('Customer', backref='customer', lazy='dynamic')

    @aggregated('customers', db.Column(db.Integer))
    def customers_count(self):
        return db.func.count()
    
    def __repr__(self):
        return '<Event %r>' % (self.name)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(16))
    message = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return '<Customer %r>' % (self.email)