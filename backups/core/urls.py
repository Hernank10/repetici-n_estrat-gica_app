from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('inventario/', views.inventario_view, name='inventario'),
    path('logros/', views.logros_view, name='logros'),
    path('ranking/', views.ranking_view, name='ranking'),
    path('amigos/', views.amigos_view, name='amigos'),
    path('mensajes/', views.mensajes_view, name='mensajes'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
]
