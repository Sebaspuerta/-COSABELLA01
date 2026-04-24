import os
import uuid
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import Producto, Categoria, AdminUser

admin_bp = Blueprint('admin', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return bool(filename) and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def get_products_image_folder():
    """
    Devuelve la ruta absoluta donde se guardarán las imágenes de productos:
    app/static/images/products/
    """
    folder = os.path.join(current_app.root_path, 'static', 'images', 'products')
    os.makedirs(folder, exist_ok=True)
    return folder


def save_image(file):
    """
    Guarda una imagen en app/static/images/products y devuelve solo el nombre del archivo.
    """
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(get_products_image_folder(), filename)
        file.save(path)
        return filename
    return None


def delete_image(filename):
    """
    Elimina una imagen física si existe.
    """
    if not filename:
        return

    path = os.path.join(get_products_image_folder(), filename)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def parse_price(value, field_name='precio'):
    """
    Convierte el valor recibido del formulario en Decimal.
    """
    if value is None or str(value).strip() == '':
        raise ValueError(f'El campo "{field_name}" es obligatorio.')

    try:
        price = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f'El campo "{field_name}" no tiene un valor válido.')

    if price < 0:
        raise ValueError(f'El campo "{field_name}" no puede ser negativo.')

    return price


def build_categoria_stats(categoria):
    """
    Construye métricas útiles por categoría para el admin.
    """
    productos = Producto.query.filter_by(categoria_id=categoria.id).all()

    total = len(productos)
    disponibles = sum(1 for p in productos if p.disponible)
    destacados = sum(1 for p in productos if p.destacado)
    en_oferta = sum(
        1 for p in productos
        if p.precio_anterior is not None and p.precio_anterior > p.precio
    )

    return {
        'categoria': categoria,
        'total': total,
        'disponibles': disponibles,
        'destacados': destacados,
        'en_oferta': en_oferta,
    }


def get_admin_sidebar_metrics():
    """
    Métricas globales para usar en varias vistas admin.
    """
    total_productos = Producto.query.count()
    productos_activos = Producto.query.filter_by(disponible=True).count()
    total_categorias = Categoria.query.count()
    destacados = Producto.query.filter_by(destacado=True).count()
    en_oferta = Producto.query.filter(
        Producto.precio_anterior.isnot(None),
        Producto.precio_anterior > Producto.precio
    ).count()

    return {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'total_categorias': total_categorias,
        'destacados': destacados,
        'en_oferta': en_oferta,
    }


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    metrics = get_admin_sidebar_metrics()
    ultimos = Producto.query.order_by(Producto.created_at.desc()).limit(6).all()
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    categorias_stats = [build_categoria_stats(c) for c in categorias]

    return render_template(
        'admin/dashboard.html',
        ultimos=ultimos,
        categorias_stats=categorias_stats,
        **metrics
    )


@admin_bp.route('/categorias')
@login_required
def categorias():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    categorias_stats = [build_categoria_stats(c) for c in categorias]
    metrics = get_admin_sidebar_metrics()

    return render_template(
        'admin/categorias.html',
        categorias_stats=categorias_stats,
        **metrics
    )


@admin_bp.route('/categorias/<int:categoria_id>/productos')
@login_required
def categoria_productos(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)

    search = request.args.get('q', '').strip()
    disponibilidad = request.args.get('disponibilidad', '').strip()
    oferta = request.args.get('oferta', '').strip()

    query = Producto.query.filter_by(categoria_id=categoria.id)

    if search:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f'%{search}%'),
                Producto.referencia.ilike(f'%{search}%')
            )
        )

    if disponibilidad == 'disponible':
        query = query.filter(Producto.disponible.is_(True))
    elif disponibilidad == 'nodisponible':
        query = query.filter(Producto.disponible.is_(False))

    if oferta == 'si':
        query = query.filter(
            Producto.precio_anterior.isnot(None),
            Producto.precio_anterior > Producto.precio
        )
    elif oferta == 'no':
        query = query.filter(
            db.or_(
                Producto.precio_anterior.is_(None),
                Producto.precio_anterior <= Producto.precio
            )
        )

    productos = query.order_by(Producto.created_at.desc()).all()
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    metrics = get_admin_sidebar_metrics()

    return render_template(
        'admin/productos.html',
        productos=productos,
        categoria_actual=categoria,
        categorias=categorias,
        search=search,
        disponibilidad=disponibilidad,
        oferta=oferta,
        **metrics
    )


@admin_bp.route('/productos')
@login_required
def productos():
    """
    Vista general de productos.
    Puede filtrar por categoría si llega ?categoria_id=
    """
    categoria_id = request.args.get('categoria_id', type=int)
    search = request.args.get('q', '').strip()
    disponibilidad = request.args.get('disponibilidad', '').strip()
    oferta = request.args.get('oferta', '').strip()

    query = Producto.query

    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    if search:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f'%{search}%'),
                Producto.referencia.ilike(f'%{search}%')
            )
        )

    if disponibilidad == 'disponible':
        query = query.filter(Producto.disponible.is_(True))
    elif disponibilidad == 'nodisponible':
        query = query.filter(Producto.disponible.is_(False))

    if oferta == 'si':
        query = query.filter(
            Producto.precio_anterior.isnot(None),
            Producto.precio_anterior > Producto.precio
        )
    elif oferta == 'no':
        query = query.filter(
            db.or_(
                Producto.precio_anterior.is_(None),
                Producto.precio_anterior <= Producto.precio
            )
        )

    items = query.order_by(Producto.created_at.desc()).all()
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    categoria_actual = Categoria.query.get(categoria_id) if categoria_id else None
    metrics = get_admin_sidebar_metrics()

    return render_template(
        'admin/productos.html',
        productos=items,
        categorias=categorias,
        categoria_actual=categoria_actual,
        search=search,
        disponibilidad=disponibilidad,
        oferta=oferta,
        **metrics
    )


@admin_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def producto_nuevo():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    categoria_preseleccionada = request.args.get('categoria_id', type=int)

    if request.method == 'POST':
        f = request.form

        try:
            nombre = f.get('nombre', '').strip()
            descripcion = f.get('descripcion', '').strip() or None
            categoria_id = f.get('categoria_id')
            material = f.get('material', '').strip() or None
            referencia = f.get('referencia', '').strip() or None

            if not nombre:
                raise ValueError('El nombre del producto es obligatorio.')

            if not categoria_id:
                raise ValueError('Debes seleccionar una categoría.')

            precio = parse_price(f.get('precio'), 'precio')

            precio_anterior_raw = f.get('precio_anterior', '').strip()
            precio_anterior = None

            if precio_anterior_raw:
                precio_anterior = parse_price(precio_anterior_raw, 'precio_anterior')
                if precio_anterior <= precio:
                    raise ValueError('El precio anterior debe ser mayor que el precio actual para marcar oferta.')

            img1 = save_image(request.files.get('imagen_principal'))
            img2 = save_image(request.files.get('imagen_2'))
            img3 = save_image(request.files.get('imagen_3'))

            p = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                precio_anterior=precio_anterior,
                categoria_id=int(categoria_id),
                destacado='destacado' in f,
                disponible='disponible' in f,
                material=material,
                referencia=referencia,
                imagen_principal=img1,
                imagen_2=img2,
                imagen_3=img3,
            )

            db.session.add(p)
            db.session.commit()

            flash(f'Producto "{p.nombre}" creado exitosamente.', 'success')
            return redirect(url_for('admin.categoria_productos', categoria_id=p.categoria_id))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al crear el producto.', 'danger')

    metrics = get_admin_sidebar_metrics()

    return render_template(
        'admin/producto_form.html',
        producto=None,
        categorias=categorias,
        categoria_preseleccionada=categoria_preseleccionada,
        **metrics
    )


@admin_bp.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def producto_editar(id):
    p = Producto.query.get_or_404(id)
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()

    if request.method == 'POST':
        f = request.form

        try:
            nombre = f.get('nombre', '').strip()
            descripcion = f.get('descripcion', '').strip() or None
            categoria_id = f.get('categoria_id')
            material = f.get('material', '').strip() or None
            referencia = f.get('referencia', '').strip() or None

            if not nombre:
                raise ValueError('El nombre del producto es obligatorio.')

            if not categoria_id:
                raise ValueError('Debes seleccionar una categoría.')

            precio = parse_price(f.get('precio'), 'precio')

            precio_anterior_raw = f.get('precio_anterior', '').strip()
            precio_anterior = None

            if precio_anterior_raw:
                precio_anterior = parse_price(precio_anterior_raw, 'precio_anterior')
                if precio_anterior <= precio:
                    raise ValueError('El precio anterior debe ser mayor que el precio actual para marcar oferta.')

            p.nombre = nombre
            p.descripcion = descripcion
            p.precio = precio
            p.precio_anterior = precio_anterior
            p.categoria_id = int(categoria_id)
            p.destacado = 'destacado' in f
            p.disponible = 'disponible' in f
            p.material = material
            p.referencia = referencia

            for field in ['imagen_principal', 'imagen_2', 'imagen_3']:
                uploaded_file = request.files.get(field)
                new_img = save_image(uploaded_file)

                if new_img:
                    old_img = getattr(p, field)
                    setattr(p, field, new_img)
                    delete_image(old_img)

            db.session.commit()
            flash(f'Producto "{p.nombre}" actualizado.', 'success')
            return redirect(url_for('admin.categoria_productos', categoria_id=p.categoria_id))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al actualizar el producto.', 'danger')

    metrics = get_admin_sidebar_metrics()

    return render_template(
        'admin/producto_form.html',
        producto=p,
        categorias=categorias,
        categoria_preseleccionada=p.categoria_id,
        **metrics
    )


@admin_bp.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def producto_eliminar(id):
    p = Producto.query.get_or_404(id)
    nombre = p.nombre
    categoria_id = p.categoria_id

    delete_image(p.imagen_principal)
    delete_image(p.imagen_2)
    delete_image(p.imagen_3)

    try:
        db.session.delete(p)
        db.session.commit()
        flash(f'Producto "{nombre}" eliminado.', 'success')
    except Exception:
        db.session.rollback()
        flash(f'No se pudo eliminar el producto "{nombre}".', 'danger')

    return redirect(url_for('admin.categoria_productos', categoria_id=categoria_id))


@admin_bp.route('/productos/<int:id>/toggle-destacado', methods=['POST'])
@login_required
def producto_toggle_destacado(id):
    p = Producto.query.get_or_404(id)

    try:
        p.destacado = not p.destacado
        db.session.commit()
        flash(
            f'Producto "{p.nombre}" {"marcado como destacado" if p.destacado else "quitado de destacados"}.',
            'success'
        )
    except Exception:
        db.session.rollback()
        flash('No se pudo actualizar el estado destacado del producto.', 'danger')

    return redirect(request.referrer or url_for('admin.productos'))


@admin_bp.route('/productos/<int:id>/toggle-disponible', methods=['POST'])
@login_required
def producto_toggle_disponible(id):
    p = Producto.query.get_or_404(id)

    try:
        p.disponible = not p.disponible
        db.session.commit()
        flash(
            f'Producto "{p.nombre}" {"marcado como disponible" if p.disponible else "marcado como no disponible"}.',
            'success'
        )
    except Exception:
        db.session.rollback()
        flash('No se pudo actualizar la disponibilidad del producto.', 'danger')

    return redirect(request.referrer or url_for('admin.productos'))