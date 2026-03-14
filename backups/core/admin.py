from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Perfil, Item, Inventario, ItemUsuario, Logro, LogroDesbloqueado, Notificacion, Amistad, Mensaje, PuntuacionDiaria

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'puntos_totales', 'nivel_maestria']
    search_fields = ['usuario__username']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'rareza', 'valor']
    list_filter = ['tipo', 'rareza']

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['usuario']
    search_fields = ['usuario__username']

@admin.register(ItemUsuario)
class ItemUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'item', 'cantidad', 'equipado']
    list_filter = ['equipado']

@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'puntos']
    list_filter = ['categoria']

@admin.register(LogroDesbloqueado)
class LogroDesbloqueadoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'logro', 'fecha_desbloqueo']
    list_filter = ['logro__categoria']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'tipo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida']

@admin.register(Amistad)
class AmistadAdmin(admin.ModelAdmin):
    list_display = ['usuario1', 'usuario2', 'estado', 'fecha_creacion']
    list_filter = ['estado']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['remitente', 'destinatario', 'contenido_corto', 'leido', 'fecha_envio']
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + "..." if len(obj.contenido) > 50 else obj.contenido

@admin.register(PuntuacionDiaria)
class PuntuacionDiariaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'puntos', 'tipo_juego', 'fecha']
    list_filter = ['tipo_juego', 'fecha']
