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
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application")

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
    sub_category: Mapped[str] = mapped_column(String(250))
    comments = relationship("Comment", back_populates="parent_blog_post")

class PlanPost(db.Model):
    __tablename__ = "plan_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="plan_posts")
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_plan_post")
    status: Mapped[str] = mapped_column(String(250), nullable=False)
    month: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[str] = mapped_column(String(250), nullable=False)



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


def select_posts(posts, category, sub_category):
    filtered_posts = []
    if posts != None:
        for post in posts:
            if post.category == category and post.sub_category == sub_category:
                filtered_posts.append(post)
    return filtered_posts

def select_plans(plans, month):
    filtered_plans = []
    if plans != None:
        for plan in plans:
            if month in plan.month:
                filtered_plans.append(plan)
    return filtered_plans


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
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    spring = select_posts(posts=all_posts, category='sparkle', sub_category='spring')[::-1][:3]
    summer = select_posts(posts=all_posts, category='sparkle', sub_category='summer')[::-1][:3]
    winter = select_posts(posts=all_posts, category='sparkle', sub_category='winter')[::-1][:3]
    autumn = select_posts(posts=all_posts, category='sparkle', sub_category='autumn')[::-1][:3]
    crochet = select_posts(posts=all_posts, category='hobby', sub_category='crochet')[::-1][:3]
    sewing = select_posts(posts=all_posts, category='hobby', sub_category='sewing')[::-1][:3]
    sashiko = select_posts(posts=all_posts, category='hobby', sub_category='sashiko')[::-1][:3]
    books = select_posts(posts=all_posts, category='self-explore', sub_category='books')[::-1][:3]
    courses = select_posts(posts=all_posts, category='self-explore', sub_category='courses')[::-1][:3]
    professional = select_posts(posts=all_posts, category='self-explore', sub_category='professional')[::-1][:3]
    all_plans = db.session.execute(db.select(PlanPost)).scalars().all()
    january = select_plans(plans=all_plans, month='january')[::-1][:3]
    february = select_plans(plans=all_plans, month='february')[::-1][:3]
    march = select_plans(plans=all_plans, month='march')[::-1][:3]
    april = select_plans(plans=all_plans, month='april')[::-1][:3]
    may = select_plans(plans=all_plans, month='may')[::-1][:3]
    june = select_plans(plans=all_plans, month='june')[::-1][:3]
    july = select_plans(plans=all_plans, month='july')[::-1][:3]
    august = select_plans(plans=all_plans, month='august')[::-1][:3]
    september = select_plans(plans=all_plans, month='september')[::-1][:3]
    october = select_plans(plans=all_plans, month='october')[::-1][:3]
    november = select_plans(plans=all_plans, month='november')[::-1][:3]
    december = select_plans(plans=all_plans, month='december')[::-1][:3]
    return render_template("index.html", spring=spring,summer=summer,winter=winter,autumn=autumn,crochet=crochet,sewing=sewing,sashiko=sashiko, books=books, courses=courses,professional=professional, january = january,february = february,march = march,april = april,may = may,june = june,july = july,august = august,september = september,october = october,november = november,december = december,logged_in=current_user.is_authenticated)


@app.route('/posts_list/<category>/<sub_category>/<logo>', methods=["GET", "POST"])
def get_select_posts(category, sub_category, logo):
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = select_posts(posts=all_posts, category=category, sub_category=sub_category)
    return render_template("post-list.html", all_posts= posts, logo=logo, category=category.capitalize(), sub_category=sub_category.capitalize(), logged_in=current_user.is_authenticated)


@app.route('/plans_list/<month>/<logo>', methods=["GET", "POST"])
def get_select_plans(month, logo):
    all_plans = db.session.execute(db.select(PlanPost)).scalars().all()
    plans = select_plans(plans=all_plans, month=month)
    return render_template("plan-list.html", all_plans=plans,logo=logo, month=month.capitalize(), logged_in=current_user.is_authenticated)


@app.route('/year_posts/<category>/<year>', methods=["GET", "POST"])
def get_year_posts(category, year):
    condition = '%'+ year
    all_posts = db.session.execute(db.select(BlogPost).where(BlogPost.date.like(condition))).scalars().all()
    spring = select_posts(posts=all_posts, category='sparkle', sub_category='spring')[::-1]
    summer = select_posts(posts=all_posts, category='sparkle', sub_category='summer')[::-1]
    winter = select_posts(posts=all_posts, category='sparkle', sub_category='winter')[::-1]
    autumn = select_posts(posts=all_posts, category='sparkle', sub_category='autumn')[::-1]
    crochet = select_posts(posts=all_posts, category='hobby', sub_category='crochet')[::-1]
    sewing = select_posts(posts=all_posts, category='hobby', sub_category='sewing')[::-1]
    sashiko = select_posts(posts=all_posts, category='hobby', sub_category='sashiko')[::-1]
    books = select_posts(posts=all_posts, category='self-explore', sub_category='books')[::-1]
    courses = select_posts(posts=all_posts, category='self-explore', sub_category='courses')[::-1]
    professional = select_posts(posts=all_posts, category='self-explore', sub_category='professional')[::-1]
    all_plans = db.session.execute(db.select(PlanPost)).scalars().all()
    january = select_plans(plans=all_plans, month='january')[::-1]
    february = select_plans(plans=all_plans, month='february')[::-1]
    march = select_plans(plans=all_plans, month='march')[::-1]
    april = select_plans(plans=all_plans, month='april')[::-1]
    may = select_plans(plans=all_plans, month='may')[::-1]
    june = select_plans(plans=all_plans, month='june')[::-1]
    july = select_plans(plans=all_plans, month='july')[::-1]
    august = select_plans(plans=all_plans, month='august')[::-1]
    september = select_plans(plans=all_plans, month='september')[::-1]
    october = select_plans(plans=all_plans, month='october')[::-1]
    november = select_plans(plans=all_plans, month='november')[::-1]
    december = select_plans(plans=all_plans, month='december')[::-1]
    return render_template("year-posts.html", spring=spring,summer=summer,winter=winter,autumn=autumn,crochet=crochet,sewing=sewing,sashiko=sashiko, books=books, courses=courses,professional=professional, january = january,february = february,march = march,april = april,may = may,june = june,july = july,august = august,september = september,october = october,november = november,december = december,category=category.capitalize(), year=year,logged_in=current_user.is_authenticated)



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


@app.route("/plan/<int:plan_id>", methods=["GET", "POST"])
def show_plan(plan_id):
    comment_form = CommentForm()
    requested_plan = db.get_or_404(PlanPost, plan_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_plan=requested_plan,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("plan.html", plan=requested_plan, logged_in=current_user.is_authenticated, form = comment_form)


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
        if form.img.data:
            file = form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img_url = f'uploads/{filename}'
        else:
            img_url = f'assets/img/home-bg2.png'
            

        new_post = BlogPost(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
            category=form.main_option.data,
            sub_category=form.sub_option.data
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
        if form.img.data:
            file = form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img_url = f'uploads/{filename}'
            month = ','.join(form.month.data)
        else:
            img_url = f'assets/img/home-bg2.png'

        new_plan = PlanPost(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
            category=form.main_option.data,
            status=form.status.data,
            month = month,
            year= form.year.data
        )
        db.session.add(new_plan)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-plan.html", form=form, logged_in=current_user.is_authenticated)



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
        else:
            post.img_url = f'assets/img/home-bg2.png'

        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)


@app.route("/edit-plan/<int:plan_id>", methods=["GET", "POST"])
@user_id_1_only
def edit_plan(plan_id):
    plan = db.get_or_404(PlanPost, plan_id)
    edit_form = CreatePlanForm(
        title=plan.title,
        body=plan.body,
        year=plan.year,
        month=plan.month,
        status=plan.status
    )
    
    if edit_form.validate_on_submit():
        plan.title = edit_form.title.data
        plan.body = edit_form.body.data
        plan.category = edit_form.main_option.data

        if edit_form.img.data:
            file = edit_form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            plan.img_url = url_for('static', filename=f'uploads/{filename}')
        else:
            plan.img_url = f'assets/img/home-bg2.png'

        db.session.commit()
        return redirect(url_for("show_plan", plan_id=plan.id))
    return render_template("make-plan.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)


@app.route("/plan-to-post/<int:plan_id>", methods=["GET", "POST"])
@user_id_1_only
def plan_to_post(plan_id):
    plan = db.get_or_404(PlanPost, plan_id)
    form = CreatePostForm(
        title=plan.title,
        body=plan.body,
        img_url=plan.img_url,
        
    )
    if form.main_option.data == 'sparkle':
        form.sub_option.choices = [('spring', 'Spring'), ('summer', 'Summer'), ('autumn', 'Autumn'),('winter', 'Winter')]
    elif form.main_option.data == 'hobby':
        form.sub_option.choices = [('crochet', 'Crochet'), ('sewing', 'Sewing'),('sashiko','Sashiko')]
    elif form.main_option.data == 'self-explore':
        form.sub_option.choices = [('books', 'Books'), ('courses', 'Courses'),('professional','Professional related')]

    if form.validate_on_submit():
        if form.img.data:
            file = form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img_url = f'uploads/{filename}'
        else:
            plan.img_url = f'assets/img/home-bg2.png'
            
        new_post = BlogPost(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y"),
            category=form.main_option.data,
            sub_category=form.sub_option.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)

# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@user_id_1_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/delete/<int:plan_id>")
@user_id_1_only
def delete_plan(plan_id):
    post_to_delete = db.get_or_404(PlanPost, plan_id)
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
