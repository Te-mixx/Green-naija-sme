from flaskr.models import User
from flaskr import app, db, bcrypt, mail
from flask import render_template, session, url_for, redirect, flash
from flaskr.forms import (RegistrationForm,
                          LoginForm, UpdateAccountForm, RequestResetForm,
                          ResetPasswordForm)
from flask import request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# Constants for fuel types and corresponding coefficients
fuel_coefficients = {
    'petrol': 2.34,
    'diesel': 2.70
}

# Constants for categories
category_coefficients = {
    'electricity': 0.439,
    'lpg': 1.56,
    'firewood': 43.03576,
    'flightDomestic': 0.24587,
    'flightInternational': 0.18362
}


@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
                                form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    company_name=form.company_name.data,
                    company_description=form.company_description.data,
                    address=form.address.data, city=form.city.data,
                    state=form.state.data, zip=form.zip_code.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Login successful", 'success')
            return redirect(next_page) if next_page else redirect(
                url_for('calculate'))
        else:
            print('error')
            flash('Invalid username or password! Try again.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/submit", methods=['POST'])
@login_required
def submit():
    data = request.json
    results = {}
    category_labels = []
    category_emissions = []
    total_prices = []
    for category, category_data in data.items():
        labels, category_values, total_price = calculate_emissions(
            category_data)
        category_labels.extend(labels)
        category_emissions.append(
            sum(category_values))  # Calculate total emissions for the category
        total_prices.append(total_price)

        results[category] = {
            'emissions': category_values,
            'total_price': total_price
        }
    total_price = int(sum(total_prices))
    emission_total = sum(category_emissions)
    total_emission = float(emission_total)

    # Store processed data in session variables
    session['category_labels'] = category_labels
    session['category_emissions'] = category_emissions
    session['total_price'] = total_price
    session['total_emission'] = round(total_emission, 2)
    return redirect(url_for('result'))


# the function handles dynamic input form correctly
def calculate_emissions(category_data):
    category_emissions = {}
    total_price = 0
    for item in category_data:
        for key, value in item.items():
            if 'litres' in value:
                litres = float(value.get(
                    'litres', 1) or 1)  # Get 'litres' value or default to 1
                price = int(value.get(
                    'price', 1) or 0)  # Get 'price' value or default to 0
                total_price += price
                if 'FuelType' in value:
                    fuel_type = value['FuelType']
                    if fuel_type in fuel_coefficients:
                        coefficient = fuel_coefficients[fuel_type]
                        category_emissions.setdefault(key, 0)
                        category_emissions[key] += (
                            litres * coefficient) / 1000
                else:
                    category = key
                    if category in category_coefficients:
                        coefficient = category_coefficients[category]
                        category_emissions.setdefault(key, 0)
                        category_emissions[key] += (
                            litres * coefficient) / 1000
            else:
                # Multiply value of key by itd corresponding category coeff,
                for category_key, category_value in item.items():
                    if category_key in category_coefficients:
                        coefficient = category_coefficients[category_key]
                        value = float(category_value.get(
                            'value', 1) or 1)  # Get value r default to 1.
                        price = float(category_value.get(
                            'price', 1) or 0)  # Get 'price'  or default to 0
                        total_price += price
                        category_emissions.setdefault(key, 0)
                        category_emissions[key] += (
                            float(value) * coefficient) / 1000
    category_labels = list(category_emissions.keys())
    category_values = list(category_emissions.values())

    return category_labels, category_values, total_price


@app.route('/result')
@login_required
def result():
    category_labels = session.get('category_labels', [])
    category_emissions = session.get('category_emissions', [])
    total_price = session.get('total_price', [])
    total_emission = session.get('total_emission')
    transportation_emission = sum(category_emissions[:5])
    energy_emission = sum(category_emissions[-4:])
    transport_percent = int((transportation_emission / sum(
        category_emissions)) * 100)
    energy_percent = int((energy_emission / sum(category_emissions)) * 100)

    return render_template('result.html', labels=category_labels,
                           data=category_emissions,
                           total_price=total_price,
                           total_emission=total_emission,
                           transportation_emission=transportation_emission,
                           energy_emission=energy_emission,
                           transport_percent=transport_percent,
                           energy_percent=energy_percent)


@app.route('/calculate', methods=['GET'])
@login_required
def calculate():
    return render_template('calculate.html', title="Calculate")


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account info updated successfully', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',
                         filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',
                           image_file=image_file, form=form, title="Account")


def send_reset_mail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@green9jasme.com.ng', recipients=[user.email])
    msg.body = f'''To reset your password, visit the link below:
    {url_for('reset_token', token=token, _external=True)}
        If you did not make this request, you can safely ignore this email.
    '''
    mail.send(msg)


@app.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_mail(user)
        flash('A password reset link has \
              been sent to your email address', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html',
                           title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid/expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',
                           title='Reset Password', form=form)


@app.route("/strategies", methods=['GET'])
@login_required
def strategies():
    return render_template('strategies.html', title='Strategies')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
