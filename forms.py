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
    title = StringField("Blog Post Title", validators=[DataRequired()])
    img = FileField("Upload Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif','heic','mov'], 'Images only!')])
    main_option = SelectField(
        'Choose a Category', 
        choices=[
            ('sparkle', 'Sparkle'),
            ('hobby', 'Hobby'),
            ('self-explore', 'Self-explore'),
            ('plan', 'Plan') 
        ],
        validators=[DataRequired()]
    )
    sub_option = SelectField('Choose a Sub-category ', choices=[])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


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
    title = StringField("Blog Post Title", validators=[DataRequired()])
    img = FileField("Upload Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif','heic','mov'], 'Images only!')])
    main_option = SelectField(
        'Choose a Category', 
        choices=[
            ('sparkle', 'Sparkle'),
            ('hobby', 'Hobby'),
            ('self-explore', 'Self-explore'),
            ('plan', 'Plan') 
        ],
        validators=[DataRequired()]
    )
    sub_option = SelectField('Choose a Sub-category ', choices=[])
    choices = MultiCheckboxField('Plan to do on:', 
            choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')])
    status=SelectField(
        'Status', choices=[
            ('done', 'Done'),
            ('plan', 'Plan'),
            ('doing', 'Doing')
        ],validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Plan")