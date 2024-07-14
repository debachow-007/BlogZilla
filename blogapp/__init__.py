from flask import Flask
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from flask_login import LoginManager # type: ignore
from flask_mail import Mail # type: ignore
from blogapp.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from blogapp.models import Post, User

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from blogapp.users.routes import users
    from blogapp.posts.routes import posts
    from blogapp.main.routes import main
    from blogapp.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    
    @app.context_processor
    def inject_counts():
        user_count = User.query.count()
        post_count = Post.query.count()
        return dict(user_count=user_count, post_count=post_count)
    
    return app