import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de Firebase
    FIREBASE_CREDENTIALS = os.path.join(
        os.path.dirname(__file__), 
        'tallersftwr2-firebase-adminsdk-fbsvc-7a5af05848.json'
    )
    FIREBASE_DATABASE_URL = 'https://tallersftwr2-default-rtdb.firebaseio.com/'
    
    # Configuración básica de la app
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5000))
    