# juegos/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    # Modelos de aventura
    AventuraNivel, ProgresoAventura,
    # Modelos de ortografía
    PreguntaOrtografia, ProgresoOrtografia,
)


@admin.register(AventuraNivel)
class AventuraNivelAdmin(admin.ModelAdmin):
    """Administración de niveles de aventura"""
    
    list_display = ['orden', 'nivel', 'titulo', 'dificultad', 'recompensa_puntos']
    list_filter = ['dificultad']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['dificultad', 'recompensa_puntos']
    ordering = ['orden']


@admin.register(ProgresoAventura)
class ProgresoAventuraAdmin(admin.ModelAdmin):
    """Administración del progreso de aventura"""
    
    list_display = ['usuario', 'nivel', 'completado', 'puntuacion', 'fecha_completado']
    list_filter = ['completado']
    search_fields = ['usuario__username', 'nivel__titulo']
    raw_id_fields = ['usuario', 'nivel']


@admin.register(PreguntaOrtografia)
class PreguntaOrtografiaAdmin(admin.ModelAdmin):
    """Administración de preguntas de ortografía"""
    
    list_display = ['palabra', 'palabra_correcta', 'categoria', 'dificultad']
    list_filter = ['categoria', 'dificultad']
    search_fields = ['palabra', 'palabra_correcta']
    list_editable = ['dificultad']


@admin.register(ProgresoOrtografia)
class ProgresoOrtografiaAdmin(admin.ModelAdmin):
    """Administración del progreso de ortografía"""
    
    list_display = ['usuario', 'categoria', 'aciertos', 'errores', 'fecha']
    list_filter = ['categoria', 'fecha']
    search_fields = ['usuario__username']