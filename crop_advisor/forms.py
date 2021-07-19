from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,FloatField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from crop_advisor.models import Approval,CropPrice,User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)],
                           render_kw={"placeholder": "Username"})
    email = StringField(validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Email address"})
    phone = StringField(validators=[DataRequired(), Length(min=10, max=10)],
                           render_kw={"placeholder": "Mobile Number"})
    city = StringField(validators=[DataRequired(), Length(min=2, max=30)],
                           render_kw={"placeholder": "City"})
    password = PasswordField(validators=[DataRequired()],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')
    
    def validate_phone(self,phone):
        try:
            number=int(phone.data)
        except ValueError: 
            raise ValidationError("Please check your mobile number")
            
    def validate_email(self, email):
        user =Approval.query.filter_by(email=email.data).first()
        user1=User.query.filter_by(email=email.data).first()
        if user or user1:
            raise ValidationError('That email is taken. Please choose a different one.')
        


class UserLoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()],render_kw={"placeholder": "Email address"})                    
    password = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class AdminLoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()],render_kw={"placeholder": "Email address"})                    
    password = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
class ChangePassword(FlaskForm):                    
    current_password = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Current Password"})
    new_password = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "New Password"})
    submit = SubmitField('Change')

class FertilizerPredict(FlaskForm):
    nitrogen=FloatField(validators=[DataRequired()])
    phosphorous=FloatField(validators=[DataRequired()])
    pottasium =FloatField(validators=[DataRequired()])
    crop=SelectField(validators=[DataRequired()])
    submit = SubmitField('Predict')
    
class CropPredict(FlaskForm):
    nitrogen=FloatField(validators=[DataRequired()])
    phosphorous=FloatField(validators=[DataRequired()])
    pottasium =FloatField(validators=[DataRequired()])
    ph =FloatField(validators=[DataRequired()])
    rainfall =FloatField(validators=[DataRequired()])
    soiltype=SelectField(validators=[DataRequired()])
    state=SelectField(validators=[DataRequired()])
    city=SelectField(validators=[DataRequired()])
    submit = SubmitField('Predict')
    
class UpdateAccountForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(validators=[DataRequired(), Email()])
    picture = FileField(validators=[FileAllowed(['jpg','jpeg', 'png'])])
    phone = StringField(validators=[DataRequired(), Length(min=10, max=10)])
    city = StringField(validators=[DataRequired(), Length(min=2, max=30)])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user =Approval.query.filter_by(email=email.data).first()
            user1=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
                
            if user1:
                raise ValidationError('That email is taken. Please choose a different one.')
                
    def validate_phone(self,phone):
        try:
            number=int(phone.data)
        except ValueError: 
            raise ValidationError("Please check your mobile number")
    