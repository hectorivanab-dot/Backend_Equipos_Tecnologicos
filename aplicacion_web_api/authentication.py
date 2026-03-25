from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from backend.firebase_config import get_firestore_client
import firebase_admin

db = get_firestore_client()

class FirebaseAuthentication(BaseAuthentication):

    # leer el token jwt del encabezado.

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization')
        if not auth_header:
            return None # no hay token
        
        # El token viene "bearer <<Token>>"

        partes = auth_header.split()

        if len(partes) != 2 or partes[0].lower() != "bearer":
            return None

        token = partes[1]

        try:
            # firebase va a validar la firma
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')

            user_profile = db.collection('usuarios').document(uid).get()
            rol = user_profile.to_dict().get('rol', 'aprendiz') if user_profile.exists else 'aprendiz'
            # usuario
            class FirebaseUser:
                def __init__(self, uid, rol, email):
                    self.uid = uid
                    self.rol = rol
                    self.email = email
                    self.is_authenticated = True
                
            return (FirebaseUser(uid, rol, email), decoded_token)
        
        except Exception as e:
            raise AuthenticationFailed(f"Token no es valido o está expirado: {str(e)}") 