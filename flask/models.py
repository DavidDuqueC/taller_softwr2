from firebase import firebase_db
from datetime import datetime

class Producto:
    """Modelo para gestión de productos e inventario"""
    collection = 'productos'
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los productos"""
        try:
            productos = firebase_db.child(Producto.collection).get()
            if productos:
                # Convertir a lista con IDs incluidos
                resultado = []
                for key, value in productos.items():
                    producto = value
                    producto['id'] = key
                    resultado.append(producto)
                return resultado
            return []
        except Exception as e:
            print(f"Error en obtener_todos: {e}")
            return []
    
    @staticmethod
    def registrar(data):
        """Registra un nuevo producto"""
        try:
            # Agregar timestamps
            data['fecha_registro'] = datetime.now().isoformat()
            data['ultima_actualizacion'] = datetime.now().isoformat()
            
            # Inicializar stock si no viene
            if 'stock' not in data:
                data['stock'] = 0
                
            resultado = firebase_db.child(Producto.collection).push(data)
            return resultado['name']
        except Exception as e:
            print(f"Error en registrar: {e}")
            return None
    
    @staticmethod
    def consultar_por_id(producto_id):
        """Consulta un producto específico por ID"""
        try:
            producto = firebase_db.child(Producto.collection).child(producto_id).get()
            if producto:
                producto['id'] = producto_id
                return producto
            return None
        except Exception as e:
            print(f"Error en consultar_por_id: {e}")
            return None
    
    @staticmethod
    def verificar_stock(producto_id, cantidad_solicitada):
        """Verifica si hay stock suficiente"""
        try:
            producto = Producto.consultar_por_id(producto_id)
            if not producto:
                return False, 0
            
            stock_actual = producto.get('stock', 0)
            return stock_actual >= cantidad_solicitada, stock_actual
        except Exception as e:
            print(f"Error en verificar_stock: {e}")
            return False, 0
    
    @staticmethod
    def actualizar_inventario(producto_id, cantidad_vendida):
        """Actualiza el stock después de una venta"""
        try:
            producto = Producto.consultar_por_id(producto_id)
            if not producto:
                return False, {'error': 'Producto no encontrado'}
            
            stock_actual = producto.get('stock', 0)
            
            if stock_actual < cantidad_vendida:
                return False, {
                    'error': 'Stock insuficiente',
                    'stock_actual': stock_actual,
                    'solicitado': cantidad_vendida
                }
            
            # Actualizar stock
            nuevo_stock = stock_actual - cantidad_vendida
            firebase_db.child(Producto.collection).child(producto_id).update({
                'stock': nuevo_stock,
                'ultima_actualizacion': datetime.now().isoformat()
            })
            
            producto_actualizado = Producto.consultar_por_id(producto_id)
            return True, producto_actualizado
            
        except Exception as e:
            print(f"Error en actualizar_inventario: {e}")
            return False, {'error': str(e)}
    
    @staticmethod
    def actualizar_producto(producto_id, data):
        """Actualiza datos del producto (no stock)"""
        try:
            data['ultima_actualizacion'] = datetime.now().isoformat()
            firebase_db.child(Producto.collection).child(producto_id).update(data)
            return Producto.consultar_por_id(producto_id)
        except Exception as e:
            print(f"Error en actualizar_producto: {e}")
            return None
    
    @staticmethod
    def eliminar_producto(producto_id):
        """Elimina un producto"""
        try:
            firebase_db.child(Producto.collection).child(producto_id).delete()
            return True
        except Exception as e:
            print(f"Error en eliminar_producto: {e}")
            return False