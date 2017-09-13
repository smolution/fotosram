# -*- coding: utf-8 -*-

from flask import redirect, url_for, flash, g
from flask_login import current_user
from threading import Thread
from AtelierApp.models import User
from functools import wraps

def required_roles(*roles):
   def wrapper(f):
      @wraps(f)
      def wrapped(*args, **kwargs):
         if get_current_user_role() not in roles:
            flash(u'K přístupu nemáte oprávnění','error')
            return redirect(url_for('index'))
         return f(*args, **kwargs)
      return wrapped
   return wrapper
 
def get_current_user_role():
    if current_user.is_authenticated:
        return g.user.role.name
    return None


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper