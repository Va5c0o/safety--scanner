from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import subprocess

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
    # Verwerk de resultaten, sla op en doorsturen naar een nieuwe pagina met de scanresultaten

    # Stuur door naar een nieuwe pagina met de resultaten van de poortscan
    return redirect(url_for('views.show_port_scan_results'))

@views.route('/results')
@login_required
def show_port_scan_results():
    # Hier toon je de resultaten van de poortscan aan de gebruiker
    return render_template('base.html')
