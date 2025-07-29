import os
import pdfkit
from decimal import Decimal

from flask import make_response
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from .forms import RegisterForm, LoginForm, FarmerPurchaseForm, SellerSaleForm
from .models import User, FarmerPurchase, SellerSale
from . import db

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/',methods=["GET", "POST"])
def index():
    form = LoginForm()
    return render_template('index.html',form=form)

@main.route('/dashboard',methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists.')
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html', form=LoginForm())

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@main.route('/buyers', methods=['GET', 'POST'])
@login_required
def buyers():
    form = FarmerPurchaseForm()
    if form.validate_on_submit():
        weight = form.weight.data
        rate = form.rate.data
        total = round(weight * rate, 2)
        # 1. Get the last purchase with highest bill number
        last_purchase = FarmerPurchase.query.order_by(FarmerPurchase.bill_no.desc()).first()

        # Handle None safely
        if last_purchase is None or last_purchase.bill_no is None:
            next_bill_no = 1
        else:
            next_bill_no = last_purchase.bill_no + 1

        new_purchase = FarmerPurchase(
            farmer_name=request.form['farmer_name'],
            fruit_name=request.form['fruit_name'],
            weight=request.form['weight'],
            rate=request.form['rate'],
            total_price=float(request.form['weight']) * float(request.form['rate']),
            date=datetime.now(),
            vehicle_no=request.form.get('vehicle_no'),
            village=request.form.get('village'),
            board_no=request.form.get('board_no'),
            quality=request.form.get('quality'),
            bill_no=next_bill_no,  # ✅ assign it here
            notes=request.form.get('notes')
        )
        db.session.add(new_purchase)
        db.session.commit()
        flash('Purchase entry saved!')
        return redirect(url_for('main.buyers'))

    purchases = FarmerPurchase.query.order_by(FarmerPurchase.date.desc()).all()
    return render_template('buyers.html', form=form, purchases=purchases)


@main.route('/seller', methods=['GET', 'POST'])
@login_required
def seller():
    form = SellerSaleForm()
    sales = SellerSale.query.order_by(SellerSale.date.desc()).all()
    if form.validate_on_submit():
        # Calculate total
        weight = Decimal(str(form.weight.data))
        rate = Decimal(str(form.rate.data))
        base = weight * rate

        commission_rate = Decimal(str(form.commission_rate.data))
        total_commission = weight * commission_rate

        tax = Decimal(str(form.tax.data))
        total_price = (base or 0) + (total_commission or 0) + (form.labour_charge.data or 0) + (form.mandi_charge.data or 0) + (tax or 0)

        transaction = SellerSale(
            seller_name=form.seller_name.data,
            quality=form.quality.data,
            weight=form.weight.data,
            rate=form.rate.data,
            commission_rate=form.commission_rate.data,
            total_commission=total_commission,
            labour_charge=form.labour_charge.data,
            mandi_charge=form.mandi_charge.data,
            tax=form.tax.data,
            total_price=total_price
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Seller transaction saved!", "success")
        return redirect(url_for("main.seller"))
    return render_template("sellers.html", form=form, sales=sales)

@main.route('/buyer-invoice/<int:id>')
@login_required
def buyer_invoice(id):
    purchase = FarmerPurchase.query.get_or_404(id)

    # Absolute paths for wkhtmltopdf compatibility
    logo_path = os.path.abspath("static/images/logo.png")
    bg_path = os.path.abspath("static/images/banana-bg.png")

    html = render_template("buyer_invoice_bill.html", purchase=purchase,
                           logo_path=logo_path, bg_path=bg_path)

    # Output PDF
    options = {
        'enable-local-file-access': None
    }

    pdf = pdfkit.from_string(html, False, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{purchase.bill_no}.pdf'
    return response


@main.route('/seller/invoice/<int:sale_id>')
@login_required
def seller_invoice(sale_id):
    sale = SellerSale.query.get_or_404(sale_id)
    html = render_template("seller_invoice.html", sale=sale)
    options = {
        'enable-local-file-access': None,
        'page-size': 'A5',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(html, False, options=options)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=seller_invoice_{sale.id}.pdf'
    return response
