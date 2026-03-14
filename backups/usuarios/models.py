from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('admin', 'Administrador'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='estudiante')
    puntos_totales = models.IntegerField(default=0)

    # Resolver conflictos de related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="usuario_set",
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_set",
        related_query_name="usuario",
    )

    def __str__(self):
        return self.username
    
    class Meta:
        # 👇 ELIMINA esta línea: default_auto_field = 'django.db.models.BigAutoField'
        pass