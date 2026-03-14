from flask import Flask, jsonify, request
from functools import wraps
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la clave del .env (sin valor por defecto)
TOKEN_SECRETO = os.environ.get('MICROSERVICES_API_KEY')

# Verificar que la clave existe (si no, error al iniciar)
if not TOKEN_SECRETO:
    raise ValueError("❌ ERROR: MICROSERVICES_API_KEY no está definida en el archivo .env")

from firebase import firebase_db
from models import Producto

app = Flask(__name__)

# ============ DECORADOR DE AUTENTICACIÓN ============
def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        # Validar que el token existe y coincide
        if not token or token != TOKEN_SECRETO:
            return jsonify({'error': 'No autorizado'}), 403
        
        return f(*args, **kwargs)
    return decorated

# ============ RUTA PÚBLICA ============
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'servicio': 'Productos MS'})

# ============ RUTAS PROTEGIDAS ============

# Obtener todos los productos
@app.route('/api/productos', methods=['GET'])
@require_token
def get_productos():
    productos = Producto.obtener_todos()
    return jsonify(productos)

# Crear un nuevo producto
@app.route('/api/productos', methods=['POST'])
@require_token
def crear_producto():
    data = request.get_json()
    
    # Validar datos mínimos
    if not data or 'nombre' not in data or 'precio' not in data:
        return jsonify({'error': 'Nombre y precio son requeridos'}), 400
    
    producto_id = Producto.registrar(data)
    return jsonify({'id': producto_id, 'message': 'Producto creado'}), 201

# Obtener un producto por ID
@app.route('/api/productos/<producto_id>', methods=['GET'])
@require_token
def get_producto(producto_id):
    producto = Producto.consultar_por_id(producto_id)
    if producto:
        return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404

# Verificar stock de un producto
@app.route('/api/productos/<producto_id>/verificar-stock', methods=['GET'])
@require_token
def verificar_stock(producto_id):
    cantidad = request.args.get('cantidad', type=int)
    
    if not cantidad:
        return jsonify({'error': 'Debe especificar cantidad'}), 400
    
    if cantidad <= 0:
        return jsonify({'error': 'La cantidad debe ser positiva'}), 400
    
    disponible, stock_actual = Producto.verificar_stock(producto_id, cantidad)
    
    return jsonify({
        'disponible': disponible,
        'stock_actual': stock_actual,
        'cantidad_solicitada': cantidad
    })

# Vender un producto (actualizar inventario)
@app.route('/api/productos/<producto_id>/vender', methods=['POST'])
@require_token
def vender(producto_id):
    data = request.get_json()
    
    if not data or 'cantidad' not in data:
        return jsonify({'error': 'Debe especificar cantidad'}), 400
    
    cantidad = data['cantidad']
    if cantidad <= 0:
        return jsonify({'error': 'La cantidad debe ser positiva'}), 400
    
    exito, resultado = Producto.actualizar_inventario(producto_id, cantidad)
    
    if exito:
        return jsonify({'message': 'Stock actualizado', 'producto': resultado})
    
    return jsonify(resultado), 400

# Actualizar producto (sin stock)
@app.route('/api/productos/<producto_id>', methods=['PUT'])
@require_token
def actualizar_producto(producto_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400
    
    # No permitir actualizar stock por esta ruta
    if 'stock' in data:
        return jsonify({'error': 'Use /vender para actualizar stock'}), 400
    
    producto = Producto.actualizar_producto(producto_id, data)
    
    if producto:
        return jsonify({'message': 'Producto actualizado', 'producto': producto})
    
    return jsonify({'error': 'Producto no encontrado'}), 404

# Eliminar producto
@app.route('/api/productos/<producto_id>', methods=['DELETE'])
@require_token
def eliminar_producto(producto_id):
    producto = Producto.consultar_por_id(producto_id)
    
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    Producto.eliminar_producto(producto_id)
    return jsonify({'message': 'Producto eliminado'})

# ============ PUNTO DE ENTRADA ============
if __name__ == '__main__':
    app.run(debug=True, port=5000)