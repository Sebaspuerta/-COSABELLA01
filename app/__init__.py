from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Inicia sesión para acceder al panel.'
    login_manager.login_message_category = 'warning'

    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app

def _seed_initial_data():
    from app.models import Categoria, AdminUser
    from werkzeug.security import generate_password_hash

    if not Categoria.query.first():
        categorias = [
            Categoria(nombre='Relojes Adultos', slug='relojes-adultos', 
                      descripcion='Elegantes relojes para hombre y mujer', icono='⌚'),
            Categoria(nombre='Relojes Niños', slug='relojes-ninos',
                      descripcion='Relojes coloridos y divertidos para los más pequeños', icono='🕐'),
            Categoria(nombre='Oro Laminado', slug='oro-laminado',
                      descripcion='Accesorios bañados en oro de 18k', icono='✨'),
            Categoria(nombre='Plata', slug='plata',
                      descripcion='Accesorios en plata 925 y plata laminada', icono='💎'),
            Categoria(nombre='Fantasía', slug='fantasia',
                      descripcion='Bisutería fina y accesorios de moda', icono='💫'),
        ]
        db.session.add_all(categorias)

    if not AdminUser.query.first():
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('cosabella2024')
        )
        db.session.add(admin)

    db.session.commit()