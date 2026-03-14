# juegos/models.py
"""
Modelos para la aplicación de juegos (Aventura y Ortografía)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


# ============================================
# MODELOS DE AVENTURA
# ============================================

class AventuraNivel(models.Model):
    """Niveles del juego de aventura"""
    
    nivel = models.IntegerField(_("número de nivel"), unique=True)
    orden = models.IntegerField(_("orden"))
    titulo = models.CharField(_("título"), max_length=200)
    descripcion = models.TextField(_("descripción"))
    historia = models.TextField(_("historia"), blank=True)
    dificultad = models.IntegerField(
        _("dificultad"),
        choices=[(1, _("Fácil")), (2, _("Medio")), (3, _("Difícil"))],
        default=1
    )
    icono = models.CharField(_("icono"), max_length=50, default='map-marker-alt')
    tiempo_limite = models.IntegerField(_("tiempo límite (segundos)"), default=30)
    recompensa_puntos = models.IntegerField(_("puntos de recompensa"), default=100)
    
    class Meta:
        verbose_name = _("nivel de aventura")
        verbose_name_plural = _("niveles de aventura")
        ordering = ['orden']
    
    def __str__(self):
        return f"{_('Nivel')} {self.nivel}: {self.titulo}"


class ProgresoAventura(models.Model):
    """Progreso del usuario en aventura"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nivel = models.ForeignKey(AventuraNivel, on_delete=models.CASCADE)
    completado = models.BooleanField(_("completado"), default=False)
    puntuacion = models.IntegerField(_("puntuación"), default=0)
    tiempo_jugado = models.DurationField(_("tiempo jugado"), default=timedelta)
    fecha_completado = models.DateTimeField(_("fecha completado"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("progreso de aventura")
        verbose_name_plural = _("progresos de aventura")
        unique_together = ['usuario', 'nivel']
    
    def __str__(self):
        return f"{self.usuario.username} - {_('Nivel')} {self.nivel.nivel}"


# ============================================
# MODELOS DE ORTOGRAFÍA
# ============================================

class PreguntaOrtografia(models.Model):
    """Preguntas de ortografía"""
    
    palabra = models.CharField(_("palabra"), max_length=100)
    palabra_correcta = models.CharField(_("palabra correcta"), max_length=100)
    opciones = models.JSONField(_("opciones"))  # Lista de opciones
    categoria = models.CharField(_("categoría"), max_length=50)
    dificultad = models.IntegerField(
        _("dificultad"),
        choices=[(1, _("Fácil")), (2, _("Medio")), (3, _("Difícil"))],
        default=1
    )
    pista = models.TextField(_("pista"), blank=True)
    
    class Meta:
        verbose_name = _("pregunta de ortografía")
        verbose_name_plural = _("preguntas de ortografía")
    
    def __str__(self):
        return self.palabra


class ProgresoOrtografia(models.Model):
    """Progreso del usuario en ortografía"""
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(_("categoría"), max_length=50)
    aciertos = models.IntegerField(_("aciertos"), default=0)
    errores = models.IntegerField(_("errores"), default=0)
    tiempo_jugado = models.DurationField(_("tiempo jugado"), default=timedelta)
    fecha = models.DateTimeField(_("fecha"), default=timezone.now)
    
    class Meta:
        verbose_name = _("progreso de ortografía")
        verbose_name_plural = _("progresos de ortografía")
    
    def __str__(self):
        return f"{self.usuario.username} - {self.categoria} - {self.fecha.date()}"