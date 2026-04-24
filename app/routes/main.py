from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    session,
    redirect,
    url_for,
    flash
)

from app.models import Producto, Categoria

main_bp = Blueprint('main', __name__)


# =========================================================
# HELPERS CARRITO
# =========================================================

def get_cart():
    return session.get('cart', {})


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


def get_cart_count():
    cart = get_cart()
    return sum(item.get('cantidad', 0) for item in cart.values())


def get_cart_total():
    cart = get_cart()
    total = 0

    for item in cart.values():
        precio = float(item.get('precio', 0))
        cantidad = int(item.get('cantidad', 0))
        total += precio * cantidad

    return total


@main_bp.app_context_processor
def inject_cart_data():
    return {
        'cart_count': get_cart_count()
    }


# =========================================================
# HOME
# =========================================================

@main_bp.route('/')
def home():
    destacados = Producto.query.filter_by(destacado=True, disponible=True).limit(8).all()
    categorias = Categoria.query.all()

    return render_template(
        'pages/home.html',
        destacados=destacados,
        categorias=categorias,
        whatsapp=current_app.config['WHATSAPP_NUMBER']
    )


# =========================================================
# CATÁLOGO
# =========================================================

@main_bp.route('/catalogo')
def catalogo():
    categoria_slug = request.args.get('categoria', '')
    busqueda = request.args.get('q', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    material = request.args.get('material', '')
    sort = request.args.get('sort', 'recientes')

    query = Producto.query.filter_by(disponible=True)

    categoria_activa = None
    if categoria_slug:
        categoria_activa = Categoria.query.filter_by(slug=categoria_slug).first_or_404()
        query = query.filter_by(categoria_id=categoria_activa.id)

    if busqueda:
        query = query.filter(Producto.nombre.ilike(f'%{busqueda}%'))

    if min_price:
        try:
            query = query.filter(Producto.precio >= float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query = query.filter(Producto.precio <= float(max_price))
        except ValueError:
            pass

    if material:
        query = query.filter(Producto.material.ilike(f'%{material}%'))

    if sort == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif sort == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    elif sort == 'nombre_asc':
        query = query.order_by(Producto.nombre.asc())
    else:
        query = query.order_by(Producto.created_at.desc())

    productos = query.all()
    categorias = Categoria.query.all()

    return render_template(
        'pages/catalogo.html',
        productos=productos,
        categorias=categorias,
        categoria_activa=categoria_activa,
        busqueda=busqueda,
        min_price=min_price,
        max_price=max_price,
        material=material,
        sort=sort,
        whatsapp=current_app.config['WHATSAPP_NUMBER']
    )


# =========================================================
# DETALLE PRODUCTO
# =========================================================

@main_bp.route('/producto/<int:producto_id>')
def producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    relacionados = Producto.query.filter(
        Producto.categoria_id == producto.categoria_id,
        Producto.id != producto.id,
        Producto.disponible == True
    ).limit(4).all()

    mensaje_wa = f"Hola! Me interesa el producto: {producto.nombre} (Ref: {producto.referencia or producto.id})"

    return render_template(
        'pages/producto.html',
        producto=producto,
        relacionados=relacionados,
        mensaje_wa=mensaje_wa,
        whatsapp=current_app.config['WHATSAPP_NUMBER']
    )


# =========================================================
# CARRITO
# =========================================================

@main_bp.route('/carrito')
def carrito():
    cart = get_cart()
    items = []
    total = 0

    for producto_id, item in cart.items():
        subtotal = float(item['precio']) * int(item['cantidad'])
        total += subtotal

        items.append({
            'id': producto_id,
            'nombre': item['nombre'],
            'precio': item['precio'],
            'cantidad': item['cantidad'],
            'imagen_principal': item.get('imagen_principal'),
            'subtotal': subtotal
        })

    return render_template(
        'pages/carrito.html',
        items=items,
        total=total,
        whatsapp=current_app.config['WHATSAPP_NUMBER']
    )


@main_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    if not producto.disponible:
        flash('Este producto no está disponible actualmente.', 'danger')
        return redirect(url_for('main.producto', producto_id=producto.id))

    try:
        cantidad = int(request.form.get('cantidad', 1))
    except ValueError:
        cantidad = 1

    if cantidad < 1:
        cantidad = 1

    cart = get_cart()
    producto_key = str(producto.id)

    if producto_key in cart:
        cart[producto_key]['cantidad'] += cantidad
    else:
        cart[producto_key] = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': cantidad,
            'imagen_principal': producto.imagen_principal
        }

    save_cart(cart)
    flash(f'"{producto.nombre}" fue agregado al carrito.', 'success')
    return redirect(url_for('main.carrito'))


@main_bp.route('/carrito/actualizar/<int:producto_id>', methods=['POST'])
def actualizar_carrito(producto_id):
    cart = get_cart()
    producto_key = str(producto_id)

    if producto_key not in cart:
        flash('El producto no existe en el carrito.', 'danger')
        return redirect(url_for('main.carrito'))

    try:
        cantidad = int(request.form.get('cantidad', 1))
    except ValueError:
        cantidad = 1

    if cantidad <= 0:
        cart.pop(producto_key, None)
        flash('Producto eliminado del carrito.', 'success')
    else:
        cart[producto_key]['cantidad'] = cantidad
        flash('Cantidad actualizada correctamente.', 'success')

    save_cart(cart)
    return redirect(url_for('main.carrito'))


@main_bp.route('/carrito/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    cart = get_cart()
    producto_key = str(producto_id)

    if producto_key in cart:
        nombre = cart[producto_key]['nombre']
        cart.pop(producto_key, None)
        save_cart(cart)
        flash(f'"{nombre}" fue eliminado del carrito.', 'success')
    else:
        flash('El producto no existe en el carrito.', 'danger')

    return redirect(url_for('main.carrito'))


@main_bp.route('/carrito/limpiar', methods=['POST'])
def limpiar_carrito():
    session.pop('cart', None)
    session.modified = True
    flash('El carrito fue vaciado.', 'success')
    return redirect(url_for('main.carrito'))


# =========================================================
# NOSOTROS
# =========================================================

@main_bp.route('/nosotros')
def nosotros():
    return render_template('pages/nosotros.html')