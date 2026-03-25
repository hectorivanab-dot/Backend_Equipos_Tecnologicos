import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication
from backend.firebase_config import get_firestore_client

db = get_firestore_client()

class PerfilImagenAPIview(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)


    def post(self, request):
        file_to_upload = request.FILES.get('imagen')

        if not file_to_upload:
            return Response({'error': 'No se envio la imagen'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = request.user.uid

            # 1. Subir la imagen a Cloudinary
            # 'folder' nos va a ordenar las imagenes

            upload_result = cloudinary.uploader.upload(
                file_to_upload,
                folder=f"adso/perfiles/{uid}/",
                public_id="foto_principal",
                overwrite=True
            )
            # 2. Obtener la URL de la imagen subida
            
            url_imagen = upload_result.get('secure_url')

            # 3. Guardar la URL en el perfil del usuario (Firestore)
            db.collection('usuarios').document(uid).update({
                'foto_url' : url_imagen
            })

            return Response({
                "mensaje": "foto actualizada correctamente",
                "url": url_imagen
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)