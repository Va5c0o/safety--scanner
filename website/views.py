from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, current_user, logout_user
from .models import Note, User  # Samenvoegen van imports voor duidelijkheid
from . import db
import json
import subprocess
import ipaddress
import datetime
# from flask_wtf.csrf import CSRFProtect
import logging

# Configuratie van het logboek
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# csrf = CSRFProtect()
# csrf.init_app(app)


# Blueprint voor de views
views = Blueprint('views', __name__)

# Route voor de homepagina
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')  # Ontvang de opmerking van HTML
        
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            # Maak een nieuwe notitie aan en voeg deze toe aan de database
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("index.html", user=current_user)

# Route om een notitie te verwijderen
@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data)  # Verwacht een JSON van INDEX.js
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

# Route voor het uitvoeren van een IP-scan
@views.route('/scan', methods=['POST'])
@login_required
def scan():
    ip_address = request.form['ipAddress']

    try:
        ip_address = ipaddress.IPv4Address(ip_address)
    except ipaddress.AddressValueError:
        flash('Ongeldig IP-adres', category='error')
        logging.error('Ongeldig IP-adres ingevoerd')  # Logboekregistratie voor ongeldig IP-adres
        return redirect(url_for('views.home'))

    command = f'nmap {ip_address}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    scan_results = result.stdout

    return render_template('results.html', scan_results=scan_results, user=current_user)

@views.route('/port_scan', methods=['POST'])
@login_required
def port_scan():
    ip_address = request.form['ipAddressPort']

    try:
        ip_address = ipaddress.IPv4Address(ip_address)
    except ipaddress.AddressValueError:
        flash('Ongeldig IP-adres', category='error')
        logging.error('Ongeldig IP-adres ingevoerd')  # Logboekregistratie voor ongeldig IP-adres
        return redirect(url_for('views.home'))

    command = f'nmap {ip_address}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    scan_results = result.stdout

    print(scan_results)  # Logging naar de console voor poortscanresultaten

    return render_template('results.html', scan_results=scan_results)

# Route voor het tonen van poortscanresultaten
@views.route('/results')
@login_required
def show_port_scan_results():
    # Toon de resultaten van de poortscan aan de gebruiker
    return render_template('base.html')

# Route voor de command line interface (CLI)
@views.route('/cli', methods=['POST'])
@login_required
def cli():
    user_input = request.form.get('userInput')  # Haal de invoer van de gebruiker op

    # Simuleer beschikbare commando's en hun uitvoer
    commands = {
        'hello': 'Hallo! Hoe gaat het?',
        'time': f'De huidige tijd is: {datetime.datetime.now().strftime("%H:%M:%S")}',
        'help': 'Beschikbare commando\'s: hello, time, help, vasco',
        'vasco': 'Hallo mijn naam is Vasco, ik ben de maker en bedenker van deze safetyscanner'
        # Voeg meer commando's toe indien nodig
    }

    response = ''
    # Controleer of het ingevoerde commando beschikbaar is
    if user_input in commands:
        response = commands[user_input]
    else:
        response = 'Ongeldig commando. Typ "help" voor beschikbare commando\'s.'

    # Zorg voor de juiste JSON-structuur met de sleutel 'response'
    return jsonify({'response': response})

# Route voor het verwijderen van een account
@views.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    user = User.query.get(user_id)  # Vind de huidige gebruiker
    
    if user:
        # Verwijder de gebruiker en zijn gerelateerde gegevens (zoals notities)
        for note in user.notes:
            db.session.delete(note)
        db.session.delete(user)
        db.session.commit()
        
        # Uitloggen van de gebruiker na verwijderen van het account
        logout_user()
        flash('Je account is succesvol verwijderd.', category='success')
        return redirect(url_for('auth.login'))  # Stuur gebruiker naar de inlogpagina of een andere bestemming

    flash('Er is iets fout gegaan. Probeer het opnieuw.', category='error')
    return redirect(url_for('views.home'))  # Stuur gebruiker naar een andere pagina bij fouten

# Route voor het bekijken en bijwerken van het gebruikersprofiel
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        
        # Haal de huidige gebruiker op
        user = current_user
        if new_email:
            user.email = new_email
        
        db.session.commit()
        flash('Profiel bijgewerkt!', category='success')
    
    return render_template('profile.html', user=current_user)
