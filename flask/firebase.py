import firebase_admin
from firebase_admin import credentials, db
from config import Config

def init_firebase():
    """Inicializa la conexión con Firebase"""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS) 
        firebase_admin.initialize_app(cred, {
            'databaseURL': Config.FIREBASE_DATABASE_URL
        })
        print("Firebase conectado correctamente")
    
    return db.reference('/')

firebase_db = init_firebase()