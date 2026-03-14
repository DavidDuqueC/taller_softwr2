import firebase_admin
from firebase_admin import credentials, db
from config import Config

def init_firebase():
    """Inicializa la conexión con Firebase"""
    try:
        # Verificar si ya está inicializado
        firebase_admin.get_app()
    except ValueError:
        # Si no está inicializado, lo inicializamos
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS) 
        firebase_admin.initialize_app(cred, {
            'databaseURL': Config.FIREBASE_DATABASE_URL
        })
        print("Firebase conectado correctamente")
    
    # Retornar referencia a la base de datos
    return db.reference('/')

# Inicializar Firebase y crear la referencia global
firebase_db = init_firebase()