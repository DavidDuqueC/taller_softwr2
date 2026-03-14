from flask import Blueprint, jsonify, request
from models import Producto

productos_bp = Blueprint('productos', __name__, url_prefix='/api/productos')

# ============================================
# REGISTRO DE PRODUCTOS
# ============================================

@productos_bp.route('/', methods=['POST'])
def registrar_producto():
    """
    Registra un nuevo producto
    Body esperado:
    {
        "nombre": "Producto X",
        "descripcion": "Descripción opcional",
        "precio": 99.99,
        "stock": 10,
        "categoria": "Electrónica"
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        campos_requeridos = ['nombre', 'precio']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({'error': f'El campo {campo} es requerido'}), 400
        
        # Validar que precio sea positivo
        if data['precio'] <= 0:
            return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
        
        # Validar stock si viene
        if 'stock' in data and data['stock'] < 0:
            return jsonify({'error': 'El stock no puede ser negativo'}), 400
        
        # Registrar producto
        producto_id = Producto.registrar(data)
        
        return jsonify({
            'mensaje': 'Producto registrado exitosamente',
            'id': producto_id,
            'producto': Producto.consultar_por_id(producto_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# CONSULTA DE PRODUCTOS
# ============================================

@productos_bp.route('/', methods=['GET'])
def consultar_productos():
    """Consulta todos los productos"""
    try:
        productos = Producto.consultar_todos()
        return jsonify({
            'total': len(productos),
            'productos': productos
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/<producto_id>', methods=['GET'])
def consultar_producto(producto_id):
    """Consulta un producto por ID"""
    try:
        producto = Producto.consultar_por_id(producto_id)
        if producto:
            return jsonify(producto)
        return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/categoria/<categoria>', methods=['GET'])
def consultar_por_categoria(categoria):
    """Consulta productos por categoría"""
    try:
        productos = Producto.consultar_por_categoria(categoria)
        return jsonify({
            'categoria': categoria,
            'total': len(productos),
            'productos': productos
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@productos_bp.route('/bajo-stock', methods=['GET'])
def productos_bajo_stock():
    """Consulta productos con stock bajo (por defecto <= 5)"""
    try:
        limite = request.args.get('limite', default=5, type=int)
        productos = Producto.productos_bajo_stock(limite)
        return jsonify({
            'limite': limite,
            'total': len(productos),
            'productos': productos
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# VERIFICACIÓN DE STOCK
# ============================================

@productos_bp.route('/<producto_id>/verificar-stock', methods=['GET'])
def verificar_stock(producto_id):
    """
    Verifica si hay stock suficiente
    Query param: cantidad (obligatorio)
    """
    try:
        cantidad = request.args.get('cantidad', type=int)
        if not cantidad:
            return jsonify({'error': 'Debe especificar la cantidad a verificar'}), 400
        
        if cantidad <= 0:
            return jsonify({'error': 'La cantidad debe ser positiva'}), 400
        
        disponible, stock_actual = Producto.verificar_stock(producto_id, cantidad)
        
        return jsonify({
            'producto_id': producto_id,
            'stock_actual': stock_actual,
            'cantidad_solicitada': cantidad,
            'disponible': disponible,
            'mensaje': 'Stock disponible' if disponible else 'Stock insuficiente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ACTUALIZACIÓN DE INVENTARIO (VENTAS)
# ============================================

@productos_bp.route('/<producto_id>/vender', methods=['POST'])
def realizar_venta(producto_id):
    """
    Actualiza el inventario después de una venta
    Body: {"cantidad": 2}
    """
    try:
        data = request.get_json()
        if not data or 'cantidad' not in data:
            return jsonify({'error': 'Debe especificar la cantidad vendida'}), 400
        
        cantidad = data['cantidad']
        if cantidad <= 0:
            return jsonify({'error': 'La cantidad debe ser positiva'}), 400
        
        exito, resultado = Producto.actualizar_inventario(producto_id, cantidad)
        
        if exito:
            return jsonify({
                'mensaje': 'Venta registrada exitosamente',
                'producto': resultado
            })
        else:
            return jsonify({
                'error': 'No se pudo realizar la venta',
                'detalle': resultado
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ACTUALIZACIÓN DE PRODUCTOS (no stock)
# ============================================

@productos_bp.route('/<producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    """
    Actualiza información del producto (precio, descripción, etc.)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        # No permitir actualizar stock por esta ruta
        if 'stock' in data:
            return jsonify({'error': 'Use /vender para actualizar stock'}), 400
        
        producto = Producto.actualizar_producto(producto_id, data)
        if producto:
            return jsonify({
                'mensaje': 'Producto actualizado',
                'producto': producto
            })
        return jsonify({'error': 'Producto no encontrado'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ELIMINACIÓN DE PRODUCTOS
# ============================================

@productos_bp.route('/<producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Elimina un producto"""
    try:
        producto = Producto.consultar_por_id(producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        Producto.eliminar_producto(producto_id)
        return jsonify({'mensaje': 'Producto eliminado exitosamente'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500