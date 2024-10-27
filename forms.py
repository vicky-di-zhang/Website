from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField, FileField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    
    
# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    img = FileField("Upload Background Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif','heic','mov'], 'Images only!')])
    main_option = SelectField(
        'Category', 
        choices=[
            ('sparkle', 'Sparkle'),
            ('hobby', 'Hobby'),
            ('self-explore', 'Self-explore'),
            ('plan', 'Plan') 
        ],
        validators=[DataRequired()]
    )
    sub_option = SelectField('Sub-category ', choices=[])
    body = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


#  Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign up")
    
#  Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField(label="Login in")


class CommentForm(FlaskForm):
    body =  CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField(label="SUbmit comment")
    
class LoginbuttonForm(FlaskForm):
    submit = SubmitField(label="Login")


# hash_and_salted_password = generate_password_hash(
#             request.form.get('password'),
#             method='pbkdf2:sha256',
#             salt_length=8


class CreatePlanForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    img = FileField("Upload Background Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif','heic','mov'], 'Images only!')])
    main_option = SelectField(
        'Category', 
        choices=[
            ('sparkle', 'Sparkle'),
            ('hobby', 'Hobby'),
            ('self-explore', 'Self-explore'),
            ('plan', 'Plan') 
        ],
        validators=[DataRequired()]
    )
    month = MultiCheckboxField('Plan to do on:', 
            choices=[('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('octorber', 'October'), ('novermber', 'November'), ('december', 'December')])
    year = StringField("Year", validators=[DataRequired()])
    status=SelectField(
        'Status', choices=[
            ('done', 'Done'),
            ('plan', 'Plan'),
            ('doing', 'Doing')
        ],validators=[DataRequired()])
    body = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")