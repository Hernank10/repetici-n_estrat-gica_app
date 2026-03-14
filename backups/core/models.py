from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================================
# MODELO PERFIL
# ============================================

class Perfil(models.Model):
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil_core'
    )
    nombre_completo = models.CharField(max_length=200, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    puntos_totales = models.IntegerField(default=0)
    nivel_maestria = models.IntegerField(default=1)
    racha_actual = models.IntegerField(default=0)
    racha_maxima = models.IntegerField(default=0)
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultima_conexion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

# ============================================
# MODELO ITEM
# ============================================

class Item(models.Model):
    TIPOS = [
        ('ESPECIAL', 'Especial'),
        ('CONSUMIBLE', 'Consumible'),
        ('COLECCIONABLE', 'Coleccionable'),
        ('MEDALLA', 'Medalla'),
    ]
    
    RAREZAS = [
        ('COMUN', 'Común'),
        ('RARO', 'Raro'),
        ('EPICO', 'Épico'),
        ('LEGENDARIO', 'Legendario'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    rareza = models.CharField(max_length=20, choices=RAREZAS, default='COMUN')
    descripcion = models.TextField()
    valor = models.IntegerField(default=0)
    
    def __str__(self):
        return self.nombre

# ============================================
# MODELO INVENTARIO
# ============================================

class Inventario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='inventario_core')
    items = models.ManyToManyField(Item, through='ItemUsuario', related_name='inventarios')
    
    def __str__(self):
        return f"Inventario de {self.usuario.username}"

# ============================================
# MODELO ITEM USUARIO
# ============================================

class ItemUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items_usuario')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='usuarios_item')
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, null=True, blank=True, related_name='items_inventario')
    cantidad = models.IntegerField(default=1)
    equipado = models.BooleanField(default=False)
    fecha_obtencion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario', 'item']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.item.nombre} x{self.cantidad}"

# ============================================
# MODELO LOGRO
# ============================================

class Logro(models.Model):
    CATEGORIAS = [
        ('AVENTURA', 'Aventura'),
        ('ORTOGRAFIA', 'Ortografía'),
        ('SOCIAL', 'Social'),
        ('ESPECIAL', 'Especial'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    puntos = models.IntegerField(default=10)
    
    def __str__(self):
        return self.nombre

# ============================================
# MODELO LOGRO DESBLOQUEADO
# ============================================

class LogroDesbloqueado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_desbloqueo = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario', 'logro']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.logro.nombre}"

# ============================================
# MODELO NOTIFICACION
# ============================================

class Notificacion(models.Model):
    TIPOS = [
        ('BIENVENIDA', 'Bienvenida'),
        ('LOGRO', 'Logro'),
        ('AMISTAD', 'Amistad'),
        ('SISTEMA', 'Sistema'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='SISTEMA')
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

# ============================================
# MODELO AMISTAD
# ============================================

class Amistad(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    usuario1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amistades1')
    usuario2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amistades2')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario1', 'usuario2']
    
    def __str__(self):
        return f"{self.usuario1.username} - {self.usuario2.username} ({self.estado})"

# ============================================
# MODELO MENSAJE
# ============================================

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"De: {self.remitente.username} Para: {self.destinatario.username}"

# ============================================
# MODELO PUNTUACION DIARIA
# ============================================

class PuntuacionDiaria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)
    tipo_juego = models.CharField(max_length=20)
    fecha = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.puntos}pts"
