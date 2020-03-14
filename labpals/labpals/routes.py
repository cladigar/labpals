import os
import pathlib
from labpals import app, db
from labpals.forms import LoginForm, GroupRegistrationForm, EditProfileForm, UploadForm, SearchForm, UserRegistrationForm
from flask import render_template, flash, redirect, url_for, request, send_from_directory, g
from flask_login import current_user, login_user, login_required, logout_user
from labpals.models import User, Result, Group
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Armand'}
    group = {'name': 'Group01',
            'location': 'Barcelona, Spain',
            'email': 'group01@gmail.com',
            'website': 'group01@labpals.com'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Barcelona'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home Page', group=group, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


def allowed_file(filename):
    return '.' in filename and filename.lower().rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm(csrf_enabled=False)
    if form.validate_on_submit():
        file = form.file.data
        pathlib.Path(app.config['UPLOAD_FOLDER'], current_user.username).mkdir(exist_ok=True)
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, filename))
            name, extension = os.path.splitext(filename)
            if db.session.query(Result.query.filter(Result.filename == name, Result.user_id == current_user.id).exists()).scalar():
                result = db.session.query(Result).filter(Result.filename == name, Result.user_id == current_user.id).one()
                result.date_modif = datetime.utcnow()
                db.session.commit()
                flash('The file has been successfully updated')
                return redirect(url_for('upload'))
            else:
                result = Result(filename=name, filetype=extension, content=os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, filename), user_id=current_user.id)
                db.session.add(result)
                db.session.commit()
                flash('The file has been successfully uploaded')
                return redirect(url_for('upload'))
    if form.errors:
        flash(form.errors, 'Danger')
    return render_template('upload.html', title="Upload File", form=form)


@app.route('/files')
@login_required
def show_files():
    user = User.query.get(current_user.id)
    files = user.results.all()
    return render_template('files.html', title="Existent Files", files=files)


@app.route('/files/<file_name><file_extension>')
@login_required
def download_file(file_name, file_extension):
    filename = f'{file_name}{file_extension}'
    user_directory = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    try:
        return send_from_directory(user_directory, filename=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/files/view/<file_name><file_extension>')
@login_required
def view_file(file_name, file_extension):
    filename = f'{file_name}{file_extension}'
    user_directory = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
    try:
        return send_from_directory(user_directory, filename=filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)

@app.route('/delete_file/<file_id>', methods=['GET', 'POST'])
@login_required
def delete_file(file_id):
    file = Result.query.get(file_id)
    filename = file.filename + file.filetype
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, filename))
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('show_files'))


@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    users, total = User.search(g.search_form.q.data, page,
                               app.config['ENTRIES_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * app.config['ENTRIES_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', users=users,
                           next_url=next_url, prev_url=prev_url)


@app.route('/groupregister', methods=['GET', 'POST'])
def groupregister():
    form = GroupRegistrationForm()
    if form.validate_on_submit():
        group = Group(groupname=form.groupname.data, email=form.email.data, location=form.location.data, website=form.website.data)
        db.session.add(group)
        db.session.commit()
        flash('Congratulations, you have registered your group!')
        return redirect(url_for('register'))
    return render_template('groupregister.html', title='Group Register', form=form)
