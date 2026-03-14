from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JuegosConfig(AppConfig):
    """Configuración de la aplicación Juegos"""

    # Nombre de la aplicación (ruta Python)
    name = 'juegos'

    # Nombre legible para humanos (aparece en el admin)
    verbose_name = 'Academia Digital - Juegos Educativos'

    # Etiqueta para internacionalización
    verbose_name_plural = 'Módulo de Juegos'

    # Orden de carga (valores más bajos cargan primero)
    default_auto_field = 'django.db.models.BigAutoField'

    # Icono para el admin (si se usa un tema personalizado)
    icon = 'fa-solid fa-gamepad'

    def ready(self):
        """
        Método llamado cuando la aplicación está lista.
        Útil para:
        - Registrar señales (signals)
        - Configurar hooks
        - Inicializar cachés
        - Programar tareas periódicas
        """
        # Importar señales para que se registren
        try:
            from . import signals
        except ImportError:
            pass

        # Inicializar datos básicos si es necesario
        self.inicializar_datos_base()

        # Programar tareas (si usas Celery)
        # self.programar_tareas_periodicas()

        print(f"✅ Aplicación '{self.verbose_name}' cargada correctamente")

    def inicializar_datos_base(self):
        """
        Inicializa datos necesarios para el funcionamiento de la app
        (items básicos, logros iniciales, etc.)
        """
        try:
            from django.db.models.signals import post_migrate
            from .management import crear_datos_base

            # Conectar señal para crear datos después de migrar
            post_migrate.connect(crear_datos_base, sender=self)

        except ImportError:
            # Si no existe el módulo de management, ignorar
            pass

    def programar_tareas_periodicas(self):
        """
        Programa tareas periódicas (requiere Celery)
        """
        try:
            from celery import current_app
            from celery.schedules import crontab

            # Ejemplo: actualizar rankings cada hora
            current_app.conf.beat_schedule.update({
                'actualizar-rankings': {
                    'task': 'juegos.tasks.actualizar_todos_los_rankings',
                    'schedule': crontab(minute=0, hour='*/1'),  # Cada hora
                },
                'verificar-logros-diarios': {
                    'task': 'juegos.tasks.verificar_logros_pendientes',
                    'schedule': crontab(minute=0, hour=0),  # A medianoche
                },
                'limpiar-notificaciones-antiguas': {
                    'task': 'juegos.tasks.limpiar_notificaciones',
                    'schedule': crontab(minute=0, hour=3),  # A las 3 AM
                },
            })
        except (ImportError, AttributeError):
            # Si no hay Celery, ignorar
            pass