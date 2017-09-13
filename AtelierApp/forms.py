# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, TextAreaField, SelectField, HiddenField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms_components import TimeField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me', default = False)

class ContactForm(FlaskForm):
    email = StringField(u'Email', validators=[DataRequired(u'Uveďte prosím Vaši emailovou adresu, abychom Vás mohli kontaktovat.'), Email()])
    name = StringField(u'Jméno', validators=[DataRequired(u'Vaše jméno, prosím'), Length(min=3)])
    surname = StringField(u'Příjmení', validators=[DataRequired(u'Vaše příjmení'), Length(min=3)])
    telephone = StringField(u'Telefon', validators=[DataRequired(u'Vyplňte prosím Vaše telefonní číslo.'), Length(min=9)])
    message = TextAreaField(u'Vaše zpráva', validators=[DataRequired(u'Nechtěli jste nám něco sdělit?'), Length(min=1)])
    
class EventContactForm(ContactForm):
    message = TextAreaField(u'Vaše zpráva fotografce')
    agree = BooleanField(u'Souhlasím s podmínkami', default = False, validators=[DataRequired(u'S podmínkami musíte souhlasit')])

class PhotoForm(FlaskForm):
    filename = HiddenField()
    category = QuerySelectField(u'Kategorie', allow_blank=True, blank_text=u'---', get_label="fullname")
    subcategory = QuerySelectField(u'Podkategorie', allow_blank=True, blank_text=u'---', get_label="fullname")
    collection = QuerySelectField(u'Kolekce', allow_blank=True, blank_text=u'---', get_label="fullname")
    featured = BooleanField(u'Featured', default= False)
    slideshow = BooleanField(u'Slideshow', default = False)
    active = BooleanField(u'Aktivní', default = True)
    save = BooleanField(u'Uložit', default = False)

class EventForm(FlaskForm):
    name = StringField(u'Název', validators=[DataRequired(u'Název události musí být vyplněn.'), Length(min=3, max=64, message=u'Název události musí mít 3-64 znaků.')])
    description = TextAreaField(u'Popis')
    location = StringField(u'Lokace', validators=[DataRequired(u'Místo akce je povinné.'), Length(max=256, message=u'Popis lokace může být maximálně 256 znaků dlouhý')])
    date = DateField(u'Datum', format='%Y-%m-%d', validators=[DataRequired(u'Vyberte datum.')])
    time = TimeField(u'Čas', validators=[DataRequired()])
    capacity = IntegerField(u'Kapacita', validators=[DataRequired(u'Vyplňte kapacitu.'), NumberRange(min=1, max=50, message=u'Kapacita 1-50 lidí')])
    active = BooleanField(u'Aktivní', default = True)
