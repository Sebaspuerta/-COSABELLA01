from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(10))

    productos = db.relationship('Producto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)

    precio = db.Column(db.Numeric(10, 2), nullable=False)
    precio_anterior = db.Column(db.Numeric(10, 2))

    imagen_principal = db.Column(db.String(255))
    imagen_2 = db.Column(db.String(255))
    imagen_3 = db.Column(db.String(255))

    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    destacado = db.Column(db.Boolean, default=False)
    disponible = db.Column(db.Boolean, default=True)

    material = db.Column(db.String(100))
    referencia = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def precio_formateado(self):
        return f"${int(self.precio):,}".replace(',', '.')

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # 🔥 ESTA ES LA QUE FALTABA
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))