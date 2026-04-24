import os
import webbrowser
from threading import Timer

from config import Config

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Forzar SQLite antes de crear la app
Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "demo.db")
Config.DEBUG = False

from app import create_app, db
from app.models import Categoria, AdminUser
from werkzeug.security import generate_password_hash


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


app = create_app()

with app.app_context():
    db.create_all()

    if not AdminUser.query.filter_by(username="admin").first():
        admin = AdminUser(
            username="admin",
            password_hash=generate_password_hash("cosabella2024")
        )
        db.session.add(admin)

    if not Categoria.query.first():
        categorias = [
            Categoria(nombre="Relojes Adultos", slug="relojes-adultos", descripcion="Relojes para adultos", icono="⌚"),
            Categoria(nombre="Relojes Niños", slug="relojes-ninos", descripcion="Relojes para niños", icono="🕐"),
            Categoria(nombre="Oro Laminado", slug="oro-laminado", descripcion="Accesorios en oro laminado", icono="✨"),
            Categoria(nombre="Plata", slug="plata", descripcion="Accesorios en plata", icono="💎"),
            Categoria(nombre="Fantasía", slug="fantasia", descripcion="Accesorios de fantasía", icono="💫"),
        ]
        db.session.add_all(categorias)

    db.session.commit()


Timer(1, open_browser).start()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)