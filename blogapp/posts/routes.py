from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required # type: ignore
from blogapp import db
from blogapp.models import Post, Comment
from blogapp.posts.forms import PostForm, CommentForm
from blogapp.posts.utils import save_picture, delete_picture
from blogapp.users.routes import users
from blogapp.main.routes import main

posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post = Post(title=form.title.data, content=form.content.data, picture=picture_file, author=current_user)
        else:
            post = Post(title=form.title.data, content=form.content.data, picture=None, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully.', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comments = Comment.query.filter_by(post=post).all()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted successfully.', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments)

@posts.route('/post/<int:post_id>/delete_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user and current_user.username != 'Admin':
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')
    return redirect(url_for('posts.post', post_id=post_id))

@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and current_user.username != 'Admin':
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            if post.picture:
                delete_picture(post.picture)
            picture_file = save_picture(form.picture.data)
            post.picture = picture_file
        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and current_user.username != 'Admin':
        abort(403)
    if post.picture:
        delete_picture(post.picture)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('main.home'))
