from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Initialiseren van de database en instellingen
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # Flask-applicatie initialiseren
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hasdaisiaediaei hajosdha'  # Geheime sleutel voor beveiliging
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # Locatie van de database
    db.init_app(app)  # Database koppelen aan de app

    # Importeren van views en auth blueprints
    from .views import views
    from .auth import auth

    # Registreren van blueprints voor verschillende routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Importeren van User en Note modellen
    from .models import User, Note

    # Creëren van de database indien deze niet bestaat
    create_database(app)

    # Initialiseren van de LoginManager voor inlogfunctionaliteit
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Loginpagina voor gebruikers
    login_manager.init_app(app)

    # Functie om gebruiker op te halen bij het inloggen
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# Functie om de database aan te maken als deze niet bestaat
def create_database(app):
    if not path.exists(DB_NAME):  # Controleer of de database bestaat
        with app.app_context():  # Context van de app om de database te maken
            db.create_all()  # Creëer de database
        print('Created Database!')
