from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductosSerializer
from .authentication import FirebaseAuthentication
from backend.firebase_config import get_firestore_client
from firebase_admin import firestore

db = get_firestore_client()

class ProductoAPIView(APIView):

    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, producto_id=None):

        uid_usuario = request.user.uid
        rol_usuario = request.user.rol

        print(rol_usuario)

        # Parametros de la consulta
        limit = int(request.query_params.get('limit', 10)) # 10 es el limite por defecto
        last_doc_id = request.query_params.get('last_doc_id')

        # Definir la consulta dependiendo el rol
        if rol_usuario == 'administrador':
            query = db.collection('api_productos')
            mensaje = "Listando como rol de administrador"
        else:
            # Se filtra por su uid
            query = db.collection('api_productos').where('usuario_id', '==', uid_usuario)
            mensaje = "Listado como USUARIO"

        #Ordenar
        query = query.order_by('fecha_creacion')

        # Logica de la paginación
        if last_doc_id:
            last_doc = db.collection('api_productos').document(last_doc_id).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        # Aplica el limite
        docs = query.limit(limit).stream()
        
        productos = []
        for doc in docs:
            producto_data = doc.to_dict()
            producto_data['id'] = doc.id
            productos.append(producto_data)

        return Response({"mensaje": mensaje,
                        "Total en pagina" : len(productos),
                        "datos": productos,
                        "next_page_token": productos[-1]['id'] if productos else None
                        }, status=status.HTTP_200_OK)

    # ==============
    # POST - Crear
    # ==============
    def post(self, request):

        serializer = ProductosSerializer(data=request.data)

        if serializer.is_valid():

            datos_validados = serializer.validated_data
            datos_validados['usuario_id'] = request.user.uid
            datos_validados['fecha_creacion'] = firestore.SERVER_TIMESTAMP

            try:
                nuevo_doc = db.collection('api_productos').add(datos_validados)
                id_generado = nuevo_doc[1].id

                return Response(
                    {
                        "mensaje": "producto creado correctamente",
                        "id": id_generado
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =================
    # PUT - Actualizar
    # =================
    def put(self, request, producto_id=None):

        if not producto_id:
            return Response(
                {"error": "El ID es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            producto_ref = db.collection('api_productos').document(producto_id)
            doc = producto_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            producto_data = doc.to_dict()

            if producto_data.get('usuario_id') != request.user.uid and request.user.rol != 'administrador':
                return Response(
                    {"error": "No tienes acceso a este producto"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ProductosSerializer(
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                producto_ref.update(serializer.validated_data)

                return Response(
                    {
                        "mensaje": f"producto {producto_id} actualizado",
                        "datos": serializer.validated_data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ==================
    # DELETE - Eliminar
    # ==================
    def delete(self, request, producto_id=None):

        if not producto_id:
            return Response(
                {"error": "El ID es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            producto_ref = db.collection('api_productos').document(producto_id)
            doc = producto_ref.get()

            if not doc.exists:
                return Response(
                    {"error": "No encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            producto_data = doc.to_dict()

            if producto_data.get("usuario_id") != request.user.uid and request.user.rol != 'administrador':
                return Response(
                    {"error": "No tienes permiso para eliminar este producto"},
                    status=status.HTTP_403_FORBIDDEN
                )

            producto_ref.delete()

            return Response(
                {"mensaje": f"producto {producto_id} eliminada"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )