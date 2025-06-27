from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm): 
    username = StringField(validators=[InputRequired(), Length(max=20)], 
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(max=20)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(max=20)], 
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(max=20)],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[InputRequired(), Length(max=20)],
                                     render_kw={"placeholder": "Confirm Password"})
    key = PasswordField(validators=[InputRequired(), Length(max=50)], 
                      render_kw={"placeholder": "Admin Key"})
    submit = SubmitField('Sign Up')