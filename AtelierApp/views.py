# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""
from os import listdir
from os.path import isfile, join
from datetime import datetime
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, flash, redirect, sessions, url_for, request, g
from AtelierApp import app, db, lm
from AtelierApp.forms import LoginForm, ContactForm, PhotoForm, EventForm, EventContactForm
from AtelierApp.decorators import required_roles
from AtelierApp.models import User, Photo, Category, Subcategory, Collection, Event, Customer
from AtelierApp.emails import send_contactForm
from config import POSTS_PER_PAGE



@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    """Renders the home page."""
    slideshow = Photo.query.filter_by(slideshow=True).all()
    
    return render_template(
        'index.html',
        title='Home Page',
        photos=slideshow,
        year=datetime.now().year
    )

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash(u'Děkujeme za zprávu, brzy se Vám ozveme.')
        send_contactForm(form)
        return redirect(url_for('index'))
    return render_template(
        'contact.html',
        title='Kontakt',
        year=datetime.now().year,
        form=form
    ).encode("utf-8")

@app.route('/prizes')
def prizes():
    return render_template(
        'prizes.html',
        title=u'Ceny focení',
        year=datetime.now().year,
    )

@app.route('/about')
@required_roles('Admin')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(u'Uživatel %s neexistuje.' % form.email.data)
            return redirect(url_for('login', **request.args))
        if not user.verify_password(form.password.data):
            flash(u'Nesprávné heslo')
            return redirect(url_for('login', **request.args))
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title='Sign In', form=form, year=datetime.now().year)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/gallery/<cat>')
@app.route('/gallery/<cat>/<int:page>')
@app.route('/gallery/<cat>/<subcat>')
@app.route('/gallery/<cat>/<subcat>/<int:page>')
def gallery(cat, subcat=None, page=1):
    category = Category.query.filter_by(name = cat).first()
    subcategories = []
    title = category.fullname
    if subcat:
        subcategory = Subcategory.query.filter_by(name = subcat).first()
        phs = Photo.query.filter_by(category_id = category.id, subcategory_id = subcategory.id).all()
        title = title + ' - ' + subcategory.fullname
    else:
        phs = Photo.query.filter_by(category_id = category.id).paginate(page, POSTS_PER_PAGE, False).items
    photos = []
    tmp = []
    for p in phs:
        if p.active:
            if(p.subcategory not in tmp):
                tmp.append(p.subcategory)
            photos.append({'filename': p.filename, 'filepath': p.filepath, 'featured': p.featured})
    if not subcat:
        for t in tmp:
            subcategories.append({'fullname': t.fullname, 'name': t.name})
    return render_template('gallery.html', photos=photos, category=category, subcategories=subcategories, title=title, year=datetime.now().year)

@app.route('/admin/gallery/add', methods=['GET', 'POST'])
@login_required
@required_roles('Admin')
def add_to_gallery():
    #photo_path = url_for('static', filename='photo/full', _external=True)
    photo_path = "\\Work\\Web\\fotosram\\AtelierApp\\AtelierApp\\AtelierApp\\static\\photo\\full"
    files = [f for f in listdir(photo_path) if isfile(join(photo_path, f))] # list of files in directory
    photos = Photo.query.all()  # list of photos in database
    photofiles = [p.filename for p in photos]   # list of filenames from photos
    unregistered_photos = [] # empty list of photos that are not in database
    for f in files:
        if f not in photofiles:
            unregistered_photos.append(f)
    forms = []
    for up in unregistered_photos:
        f = PhotoForm(prefix=up)
        f.category.query = Category.query.order_by(Category.fullname)
        f.subcategory.query = Subcategory.query.order_by(Subcategory.fullname)
        f.collection.query = Collection.query.order_by(Collection.fullname)
        f.filename.data = up
        forms.append(f)
    for f in forms:
        if f.validate_on_submit():
            photo = Photo(filename=f.filename.data,
                          filepath=photo_path,
                          slideshow=f.slideshow.data,
                          active=f.active.data,
                          featured=f.featured.data,
                          category = f.category.data,
                          subcategory=f.subcategory.data,
                          collection=f.collection.data)

            flash('%s validated' % str(photo))
            db.session.add(photo)
            db.session.commit()
            return redirect(url_for('add_to_gallery', **request.args))
    return render_template('add-to-gallery.html', photos_forms=zip(unregistered_photos, forms))

@app.route('/admin/gallery')
@login_required
@required_roles('Admin')
def admin_gallery():
    phs = Photo.query.join(Category).join(Subcategory).order_by(Photo.active.desc()).all()
    photos = []
    for p in phs:
        photos.append({'filename': p.filename,
                      'filepath': p.filepath,
                      'active': p.active,
                      'slideshow': p.slideshow,
                      'featured': p.featured,
                      'category': p.category.fullname,
                      'subcategory': p.subcategory.fullname,
                      'collection': None,
                      'id': p.id
                     })
    return render_template('admin-gallery.html', photos=photos, title=u'Správa fotografií', year=datetime.now().year)

@app.route('/admin/gallery/photo/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@required_roles('Admin')
def edit_photo(id):
    p = Photo.query.filter_by(id=id).first()
    f=PhotoForm(obj=p)
    f.category.query = Category.query.order_by(Category.fullname)
    f.subcategory.query = Subcategory.query.order_by(Subcategory.fullname)
    f.collection.query = Collection.query.order_by(Collection.fullname)

    if f.validate_on_submit():
        p.slideshow=f.slideshow.data
        p.active=f.active.data
        p.featured=f.featured.data
        p.category = f.category.data
        p.subcategory=f.subcategory.data
        p.collection=f.collection.data

        db.session.commit()
        flash('%s upraven' % str(p))
        return redirect(url_for('admin_gallery', **request.args))

    return render_template('edit-photo.html', photo=p, form=f, title=p.filename, year=datetime.now().year)


@app.route('/events')
def events():
    evs = Event.query.filter_by(active=True).order_by(Event.date.asc()).all()
    events = []
    for e in evs:
        events.append({'name': e.name,
                      'description': e.description,
                      'active': e.active,
                      'location': e.location,
                      'date': e.date,
                      'time': e.time,
                      'capacity': e.capacity,
                      'free': '',
                      'id': e.id
                     })
    return render_template('events.html', events=events, title=u'Správa událostí', year=datetime.now().year)


@app.route('/events/<int:id>', methods=['GET', 'POST'])
def apply_event(id):
    event = Event.query.filter_by(id=id).first()
    form = EventContactForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data + ' ' + form.surname.data,
                            email=form.email.data,
                            phone=form.telephone.data,
                            message=form.message.data,
                            event_id=event.id)
        db.session.add(customer)
        db.session.commit()
        flash(u'Děkujeme za Váš zájem o naše služby. Brzy se Vám ozveme.')
        send_contactForm(form)
        return redirect(url_for('index'))
    return render_template('apply-event.html', event=event, form=form, title=event.name, year=datetime.now().year)



@app.route('/admin/events')
@login_required
@required_roles('Admin')
def admin_events():
    evs = Event.query.order_by(Event.active.desc()).all()
    events = []
    for e in evs:
        events.append({'name': e.name,
                      'description': e.description,
                      'active': e.active,
                      'location': e.location,
                      'date': e.date,
                      'time': e.time,
                      'capacity': e.capacity,
                      'free': e.capacity-e.customers.count(),
                      'id': e.id
                     })
    return render_template('admin-events.html', events=events, title=u'Správa událostí', year=datetime.now().year)


@app.route('/admin/events/add', methods=['GET', 'POST'])
@login_required
@required_roles('Admin')
def add_event():
    f = EventForm()
    if f.validate_on_submit():
        event = Event(name = f.name.data,
                      description = f.description.data,
                      location = f.location.data,
                      date =  f.date.data,
                      time = f.time.data,
                      capacity = f.capacity.data,
                      active = f.active.data)
        db.session.add(event)
        db.session.commit()
        flash(u'Vytvořena událost %s' % str(event))
        return redirect(url_for('admin_events', **request.args))
    return render_template('add-event.html', form = f, title=u'Přidání události', year=datetime.now().year)


@app.route('/admin/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@required_roles('Admin')
def edit_event(id):
    event = Event.query.filter_by(id=id).first()
    f = EventForm(obj=event)
    if f.validate_on_submit():
        event.name = f.name.data
        event.description = f.description.data
        event.location = f.location.data
        event.date =  f.date.data
        event.time = f.time.data
        event.capacity = f.capacity.data
        event.active = f.active.data
        
        db.session.commit()
        flash(u'Událost %s změněna' % str(event))
        return redirect(url_for('admin_events', **request.args))
    return render_template('edit-event.html', form = f, title=u'Editace události', year=datetime.now().year)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
