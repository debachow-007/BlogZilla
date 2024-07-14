from flask import Blueprint, redirect, url_for, render_template, flash, request
from blogapp import db, bcrypt
from blogapp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required # type: ignore
from blogapp.users.utils import save_picture, delete_picture, send_reset_email
from blogapp.models import User, Post, Comment

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully.', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route('/account/remove_image')
@login_required
def remove_image():
    delete_picture(current_user.image_file)
    current_user.image_file = 'default.jpg'
    db.session.commit()
    flash('Profile picture removed.', 'success')
    return redirect(url_for('users.account'))

@users.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = request.form.get('user_id')
    if not user_id:
        flash('No user ID provided.', 'danger')
        return redirect(url_for('main.home'))

    # Ensure the current user is allowed to delete this account
    if not current_user.id == int(user_id) and not current_user.username == 'Admin':
        flash('Unauthorized to delete this account.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.home'))
    
    comments = Comment.query.filter_by(user_id=user.id).all()
    for comment in comments:
        db.session.delete(comment)
    
    posts = Post.query.filter_by(user_id=user.id).all()
    for post in posts:
        if post.picture:
            delete_picture(post.picture, 'static/post_pics')
        db.session.delete(post)
    
    if user.image_file != 'default.jpg':
        delete_picture(user.image_file)
        
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('main.home'))

@users.route('/user/<string:username>', methods=['GET', 'POST'])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('users.login'))
        else:
            flash('Email does not exist. Please register.', 'danger')
            return redirect(url_for('users.register'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)