# Importeer de vereiste modules en classes
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import jsonify
import datetime

# Initialiseer de blueprint voor authenticatie
auth = Blueprint('auth', __name__)

# Route voor het inloggen van gebruikers
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Controleer of het een POST-verzoek is om in te loggen
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Zoek de gebruiker op basis van het e-mailadres
        user = User.query.filter_by(email=email).first()
        if user:
            # Controleer of het wachtwoord overeenkomt met de gehashte versie in de database
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)  # Log de gebruiker in en onthoud deze sessie
                return redirect(url_for('views.home'))  # Doorverwijzen naar de homepagina na succesvol inloggen
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    # Laad het inlogformulier
    return render_template("login.html", user=current_user)

# Route voor uitloggen van gebruikers
@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Uitloggen van de huidige gebruiker
    return redirect(url_for('auth.login'))  # Terug naar het inlogscherm na uitloggen

# Route voor het aanmaken van een nieuwe gebruiker
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Verkrijg de gegevens van het registratieformulier
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 2 characters', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 7 characters!', category='error')
        else:
            # Maak een nieuwe gebruiker aan met de ingevoerde gegevens
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Log de nieuwe gebruiker in
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

# Route voor de command line interface (CLI) na inloggen
@auth.route('/cli', methods=['GET', 'POST'])
@login_required
def cli():
    if request.method == 'POST':
        user_input = request.form.get('userInput')  # Ontvang de invoer van de gebruiker
        
        # Simuleer en reageer op gebruikersinvoer met vooraf gedefinieerde antwoorden
        responses = {
            'hallo': 'Hallo! Hoe gaat het?',
            'tijd': datetime.datetime.now().strftime("%H:%M:%S"),
            'help': 'Beschikbare commando\'s: hallo, tijd, help, vasco',
            'vasco': 'Hallo mijn naam is Vasco, ik ben de maker en bedenker van deze safetyscanner'
        }
        
        # Zoek de bijbehorende reactie op basis van de invoer
        response = responses.get(user_input.lower(), 'Commando niet herkend. Typ "help" voor beschikbare commando\'s.')
        
        # Geef het antwoord terug als JSON
        return jsonify({'response': response})
    
    return render_template('cli.html', user=current_user)  # Laad de CLI-pagina
