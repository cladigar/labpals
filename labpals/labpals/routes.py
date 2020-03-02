import os
from labpals import app, db
from labpals.forms import LoginForm, RegistrationForm, EditProfileForm, UploadForm
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
from labpals.models import User, Result
from werkzeug.urls import url_parse
from werkzeug import secure_filename
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Armand'}
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
    return render_template('index.html', title='Home Page', posts=posts)

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
    form = RegistrationForm()
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
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

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
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        name, extension = os.path.splitext(filename)
        result = Result(filename=name, filetype=extension, content=os.path.join(app.config['UPLOAD_FOLDER'], filename), group_id='none_yet', user_id=current_user.id)
        db.session.add(result)
        db.session.commit()
        flash('The file has been succesfully uploaded')
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

@app.route('/files/<pdf_id>')
@login_required
def download_pdf(pdf_id):
    filename = f'{pdf_id}.pdf'
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/files/view/<pdf_id>')
@login_required
def view_pdf(pdf_id):
    filename = f'{pdf_id}.pdf'
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)
