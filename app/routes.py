from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, AddTransactionForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Transaction
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = AddTransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            date = form.date.data,
            buy_currency = form.buy_currency.data,
            buy_amount = form.buy_amount.data,
            sell_currency = form.sell_currency.data,
            sell_amount = form.sell_amount.data,
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully')
    transactions = Transaction.query.filter_by(user_id=current_user.email)
    return render_template('transactions.html', title='Transactions', form=form, transactions=transactions)