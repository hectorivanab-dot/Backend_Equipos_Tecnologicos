from django.urls import path
from .views import ProductoAPIView
from .views_auth import RegistroAPIView, LoginAPIView
from .views_perfil import PerfilImagenAPIview
from .solicitudes_views import SolicitudAPIView

urlpatterns = [
    path('auth/registro/', RegistroAPIView.as_view(), name='api_registro'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),

    path('productos/', ProductoAPIView.as_view(), name='api_productos'),
    path('productos/<str:producto_id>/', ProductoAPIView.as_view(), name='api_productos_detalle'),

    path('perfil/foto/', PerfilImagenAPIview.as_view(), name='api_perfil_foto'),
    path('solicitudes/', SolicitudAPIView.as_view(), name='solicitudes'),
]