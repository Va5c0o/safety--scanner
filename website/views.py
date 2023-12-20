from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, current_user, logout_user
from .models import Note
from .models import User
from . import db
import json
import subprocess
import datetime

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("index.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/scan', methods=['POST'])
@login_required
def scan():
    ip_address = request.form['ipAddress']
    command = f'nmap {ip_address}'  # Voer de nmap-scan uit met het ingevoerde IP
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Je zou hier de resultaten kunnen verwerken en doorsturen naar de resultatenpagina
    # Maar je moet het resultaat eerst aan de sjabloon doorgeven
    scan_results = result.stdout  # Voorbeeld: result.stdout bevat de uitvoer van de scan
    
    # Haal de huidige gebruiker op voor doorgeven aan de sjabloon
    user = current_user
    
    # Stuur de resultaten naar de resultatenpagina en geef de user door
    return render_template('results.html', scan_results=scan_results, user=user)


@views.route('/port_scan', methods=['POST'])
@login_required
def port_scan():
    ip_address = request.form['ipAddressPort']
    command = f'nmap {ip_address}'  # Voer de nmap-scan uit met het ingevoerde IP voor de poortscan
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    scan_results = result.stdout  # Ontvang de uitvoer van de poortscan

    # Voeg deze regel toe om de resultaten te controleren in de terminal/console
    print(scan_results)

    # Stuur de scanresultaten naar de 'results.html'-pagina
    return render_template('results.html', scan_results=scan_results)

@views.route('/results')
@login_required
def show_port_scan_results():
    # Hier toon je de resultaten van de poortscan aan de gebruiker
    return render_template('base.html')

@views.route('/cli', methods=['POST'])
@login_required
def cli():
    user_input = request.form.get('userInput')  # Haal de invoer van de gebruiker op

    # Simuleer een lijst van beschikbare commando's en hun uitvoer
    commands = {
        'hello': 'Hallo! Hoe gaat het?',
        'time': f'De huidige tijd is: {datetime.datetime.now().strftime("%H:%M:%S")}',
        'help': 'Beschikbare commando\'s: hello, time, help, vasco',
        'vasco': 'Hallo mijn naam is Vasco, ik ben de maker en bedenker van deze safetyscanner'
        # Voeg hier meer commando's toe indien gewenst
    }

    response = ''
    # Controleer of het ingevoerde commando in de lijst van beschikbare commando's staat
    if user_input in commands:
        response = commands[user_input]
    else:
        response = 'Ongeldig commando. Typ "help" voor beschikbare commando\'s.'

    # Zorg ervoor dat de JSON de juiste structuur heeft met de sleutel 'response'
    return jsonify({'response': response})

@views.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    # Vind de huidige gebruiker op basis van de user_id
    user = User.query.get(user_id)
    
    # Verwijder de gebruiker en zijn gerelateerde gegevens (zoals notities)
    if user:
        for note in user.notes:
            db.session.delete(note)
        db.session.delete(user)
        db.session.commit()
        
        # Uitloggen van de gebruiker na het verwijderen van het account
        logout_user()
        flash('Je account is succesvol verwijderd.', category='success')
        return redirect(url_for('auth.login'))  # Stuur gebruiker naar de inlogpagina of een andere gewenste bestemming

    flash('Er is iets fout gegaan. Probeer het opnieuw.', category='error')
    return redirect(url_for('views.home'))  # Stuur gebruiker naar een andere pagina bij fouten

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