import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth, firestore
from backend.firebase_config import get_firestore_client

db = get_firestore_client()

class RegistroAPIView(APIView):
    # Endpoiny publico para registrar usuarios
    # No requiere autenticación
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        rol = request.data.get('rol')

        if not email or not password or not rol:
            return Response({"error":"Email, rol y contraseña son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear el usuario en Firebase Authentication
            user = auth.create_user(email=email, password=password)

            # Crear un documento en Firestore para el usuario
            db.collection('usuarios').document(user.uid).set({
                "email": email,
                "rol": rol,
                "fecha_registro": firestore.SERVER_TIMESTAMP
            })

            return Response({"mensaje":"Usuario registrado exitosamente","uid": user.uid}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        email = request.data.get('email')
        password = request.data.get('password')
        apiKey = os.getenv('FIREBASE_API_KEY')

        if not email or not password:
            return Response(
                {"error": "Email y contraseña son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={apiKey}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()  # 👈 SIEMPRE definimos data aquí

            if response.status_code == 200:
                return Response({
                    "mensaje": "Inicio de sesión exitoso",
                    "token": data["idToken"],
                    "uid": data["localId"]
                }, status=status.HTTP_200_OK)

            else:
                error_msg = data.get("error", {}).get("message", "Credenciales inválidas")

                return Response({
                    "error": error_msg
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )