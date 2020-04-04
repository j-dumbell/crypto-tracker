from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.fields.html5 import DateField
from app.models import User, get_all_currencies
import datetime


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddTransactionForm(FlaskForm):
    date = DateField('DatePicker', format='%Y-%m-%d')
    buy_currency = SelectField('Buy currency', choices=get_all_currencies())
    buy_amount = FloatField('Buy amount', validators=[DataRequired()])
    sell_currency = SelectField('Sell currency', choices=get_all_currencies())
    sell_amount = FloatField('Sell amount', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        seen = set()
        for field in [self.buy_currency, self.sell_currency]:
            if field.data in seen:
                field.errors.append('Please select distinct currencies')
                result = False
            else:
                seen.add(field.data)
        return result

    def validate_date(self, date):
        if date.data > datetime.date.today():
            raise ValidationError('Date in future!')
