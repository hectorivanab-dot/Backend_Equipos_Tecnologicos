from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .authentication import FirebaseAuthentication
from backend.firebase_config import get_firestore_client
from firebase_admin import firestore

db = get_firestore_client()

class SolicitudAPIView(APIView):

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    # =====================
    # POST - Crear solicitud
    # =====================
    def post(self, request):

        uid_usuario = request.user.uid

        data = request.data

        producto_id = data.get("producto_id")
        cantidad = data.get("cantidad")

        if not producto_id or not cantidad:
            return Response(
                {"error": "producto_id y cantidad son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verificar que el producto exista
            producto_ref = db.collection('api_productos').document(producto_id)
            producto_doc = producto_ref.get()

            if not producto_doc.exists:
                return Response(
                    {"error": "El producto no existe"},
                    status=status.HTTP_404_NOT_FOUND
                )

            producto_data = producto_doc.to_dict()

            # Crear la solicitud
            nueva_solicitud = {
                "producto_id": producto_id,
                "nombre_producto": producto_data.get("nombre"),
                "cantidad": cantidad,
                "usuario_id": uid_usuario,
                "estado": "pendiente",
                "fecha_creacion": firestore.SERVER_TIMESTAMP
            }

            doc_ref = db.collection('api_solicitudes').add(nueva_solicitud)

            return Response(
                {
                    "mensaje": "Solicitud creada correctamente",
                    "id": doc_ref[1].id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # =====================
    # GET - Listar solicitudes
    # =====================
    def get(self, request):

        uid_usuario = request.user.uid
        rol_usuario = request.user.rol

        if rol_usuario == "administrador":
            query = db.collection('api_solicitudes')
        else:
            query = db.collection('api_solicitudes').where('usuario_id', '==', uid_usuario)

        query = query.order_by('fecha_creacion')

        docs = query.stream()

        solicitudes = []

        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            solicitudes.append(data)

        return Response(
            {
                "total": len(solicitudes),
                "datos": solicitudes
            },
            status=status.HTTP_200_OK
        )