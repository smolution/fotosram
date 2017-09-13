# -*- coding: utf-8 -*-

from flask_mail import Message
from AtelierApp import mail, app
from config import ADMINS
from flask import render_template
from threading import Thread
from AtelierApp.decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

def send_contactForm(form):
    email = form.email.data
    name = form.name.data
    surname = form.surname.data
    phone = form.telephone.data
    message = form.message.data
    send_email('Vzkaz z webu od %s %s' % (name, surname), email, ADMINS, render_template("contact-form-mail.txt", form=form), render_template("contact-form-mail.html", form=form))

def send_eventContactForm(form, event):
    email = form.email.data
    name = form.name.data
    surname = form.surname.data
    phone = form.telephone.data
    message = form.message.data
    send_email(u'Focení - %s, %s' % (event.name, event.date), email, ADMINS, render_template("event-form-mail.txt", form=form, event=event), render_template("event-form-mail.html", form=form, event=event))
