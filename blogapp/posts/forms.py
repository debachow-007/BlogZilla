from flask_wtf import FlaskForm # type: ignore
from flask_wtf.file import FileField, FileAllowed # type: ignore
from wtforms import StringField, SubmitField, TextAreaField, FileField # type: ignore
from wtforms.validators import DataRequired # type: ignore

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')
    
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')