from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm,LoginForm,RegisterForm,CommentForm,LoginbuttonForm,CreatePlanForm
from functools import wraps
from flask import abort
import os
from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','heic','mov'}

ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

def user_id_1_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)  
        return f(*args, **kwargs)
    return decorated_function


# Create a User table for all your registered users. 
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    blog_posts = relationship("BlogPost", back_populates="author")  # 对应 BlogPost 的 back_populates
    plan_posts = relationship("PlanPost", back_populates="author")  # 对应 PlanPost 的 back_populates

    comments = relationship("Comment", back_populates="comment_author")

# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="blog_posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    sub_category: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_blog_post")

class PlanPost(db.Model):
    __tablename__ = "plan_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="plan_posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    sub_category: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_plan_post")
    statues: Mapped[str] = mapped_column(String(250), nullable=False)
    monates: Mapped[str] = mapped_column(String(500), nullable=False)



class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    blog_post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"), nullable=True)
    plan_post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("plan_posts.id"), nullable=True)
    parent_blog_post = relationship("BlogPost", back_populates="comments")
    parent_plan_post = relationship("PlanPost", back_populates="comments")
    date: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()


# Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == request.form.get("email")))
        user = result.scalar()
        if user:
            flash("You have signed up.")
            return redirect(url_for("register"))
        else:
            hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
            new_user = User(
                name = request.form.get("name"),
                email = request.form.get("email"),
                password = hash_and_salted_password ,
            )

            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
    return render_template("register.html",form=form, buttonform = LoginbuttonForm(), logged_in=current_user.is_authenticated)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email==form.email.data))
        user=result.scalar()
        if not user:
            flash("You haven't register")
            return redirect(url_for("login"))
        
        if check_password_hash(user.password,form.password.data):
            login_user(user)
            return redirect(url_for("get_all_posts"))
        
        else:
            flash("Wrong password.")
            return redirect(url_for("login"))
    
    return render_template("login.html",form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    posts_sparkle = db.session.execute(db.select(BlogPost).where(BlogPost.category =='Sparkle')).scalars().all()
    posts_hobby = db.session.execute(db.select(BlogPost).where(BlogPost.category =='Hobby')).scalars().all()
    posts_self = db.session.execute(db.select(BlogPost).where(BlogPost.category =='Self-explore')).scalars().all()
    posts_plan = db.session.execute(db.select(BlogPost).where(BlogPost.category =='Plan')).scalars().all()
    return render_template("index.html", sparkle=posts_sparkle,hobby=posts_hobby,self=posts_self,plan=posts_plan, logged_in=current_user.is_authenticated)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, logged_in=current_user.is_authenticated, form = comment_form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post/", methods=["GET", "POST"])
@user_id_1_only
def add_new_post():
    form = CreatePostForm()
    if form.main_option.data == 'sparkle':
        form.sub_option.choices = [('spring', 'Spring'), ('summer', 'Summer'), ('autumn', 'Autumn'),('winter', 'Winter')]
    elif form.main_option.data == 'hobby':
        form.sub_option.choices = [('crochet', 'Crochet'), ('sewing', 'Sewing'),('sashiko','Sashiko')]
    elif form.main_option.data == 'self-explore':
        form.sub_option.choices = [('books', 'Books'), ('courses', 'Courses'),('professional','Professional related')]
    elif form.main_option.data == 'plan':
        form.sub_option.choices = [('carrot', 'Carrot'), ('potato', 'Potato')]


    if form.validate_on_submit():
        file = form.img.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        img_url = url_for('static', filename=f'uploads/{filename}')

        new_post = BlogPost(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
            main_option=form.main_option.data,
            sub_option=form.sub_option.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)



@app.route("/new-plan/", methods=["GET", "POST"])
@user_id_1_only
def add_new_plan():
    form = CreatePlanForm()
    if form.validate_on_submit():
        file = form.img.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        img_url = url_for('static', filename=f'uploads/{filename}')

        new_post = BlogPost(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
            main_option=form.main_option.data,
            sub_option=form.sub_option.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@user_id_1_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body
    )
    
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.body = edit_form.body.data
        post.category = edit_form.main_option.data
        post.sub_category = edit_form.sub_option.data

        if edit_form.img.data:
            file = edit_form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            post.img_url = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@user_id_1_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
