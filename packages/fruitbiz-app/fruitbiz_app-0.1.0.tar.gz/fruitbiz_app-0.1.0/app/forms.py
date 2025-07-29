from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, SubmitField, DecimalField
from wtforms.validators import InputRequired, Length, EqualTo, DataRequired, Optional


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class FarmerPurchaseForm(FlaskForm):
    farmer_name = StringField('Farmer Name', validators=[InputRequired()])
    fruit_name = StringField('Fruit Name', validators=[InputRequired()])
    weight = FloatField('Weight (Quintal)', validators=[InputRequired()])
    rate = FloatField('Rate per Quintal', validators=[InputRequired()])
    submit = SubmitField('Add Purchase')

class SellerSaleForm(FlaskForm):
    seller_name = StringField('Seller Name', validators=[DataRequired()])
    fruit_name = StringField('Fruit Name', validators=[DataRequired()])
    quality = StringField('Quality', validators=[Optional()])
    weight = DecimalField('Weight (kg)', validators=[DataRequired()])
    rate = DecimalField('Rate (Rs/Quintal)', validators=[DataRequired()])
    commission_rate = FloatField('Commission (Rs/Quintal)', validators=[InputRequired()])
    labour_charge = DecimalField('Labour Charge (Rs)', validators=[Optional()])
    mandi_charge = DecimalField('Mandi Charge (Rs)', validators=[Optional()])
    tax = DecimalField('Tax (Rs)', validators=[Optional()])
    submit = SubmitField('Add Sale')


