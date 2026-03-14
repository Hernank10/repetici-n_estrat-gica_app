from django.urls import path
from . import views

app_name = 'juegos'

urlpatterns = [
    path('aventura/', views.aventura_list_view, name='aventura_list'),
    path('aventura/<int:nivel_id>/', views.aventura_jugar_view, name='aventura_jugar'),
    path('ortografia/', views.ortografia_categorias_view, name='ortografia_categorias'),
    path('ortografia/jugar/', views.ortografia_jugar_view, name='ortografia_jugar'),
    path('ortografia/jugar/<str:categoria>/', views.ortografia_jugar_view, name='ortografia_jugar_categoria'),
]
