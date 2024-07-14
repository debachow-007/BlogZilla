from flask import Blueprint, flash, render_template, url_for, redirect, request
from blogapp.models import User, Post


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/search')
def search():
    username = request.args.get('username')
    if not username:
        flash("Please enter a username to search.", 'danger')
        return redirect(url_for('main.home'))

    user = User.query.filter_by(username=username).first()

    if user:
        return redirect(url_for('users.user_posts', username=username))
    else:
        flash(f"User '{username}' not found.", 'danger')
        return redirect(url_for('main.home'))