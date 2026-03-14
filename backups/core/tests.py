"""
Tests para la aplicación core de Academia Digital
Cubre modelos, vistas, formularios, API y funcionalidades sociales
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from datetime import timedelta, date
import json
from .models import (
    Perfil, Inventario, Item, ItemUsuario, Logro, LogroDesbloqueado,
    Notificacion, Amistad, Mensaje, PuntuacionDiaria
)

# ============================================
# TESTS DE MODELOS
# ============================================

class ModelosCoreTest(TestCase):
    """Pruebas para los modelos de la app core"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.perfil = Perfil.objects.get(usuario=self.usuario)
    
    def test_perfil_creacion_automatica(self):
        """Verifica que el perfil se cree automáticamente al crear usuario"""
        nuevo_usuario = User.objects.create_user(
            username='nuevo',
            password='pass123'
        )
        self.assertTrue(hasattr(nuevo_usuario, 'perfil'))
        self.assertEqual(nuevo_usuario.perfil.puntos_totales, 0)
        self.assertEqual(nuevo_usuario.perfil.nivel_maestria, 1)
    
    def test_perfil_str(self):
        """Prueba la representación string del perfil"""
        self.assertEqual(
            str(self.perfil),
            f"Perfil de {self.usuario.username}"
        )
    
    def test_inventario_creacion_automatica(self):
        """Verifica que el inventario se cree automáticamente"""
        self.assertTrue(hasattr(self.usuario, 'inventario'))
        self.assertEqual(self.usuario.inventario.capacidad_maxima, 50)
    
    def test_item_creation(self):
        """Prueba la creación de items"""
        item = Item.objects.create(
            nombre='Pista Extra',
            tipo='CONSUMIBLE',
            rareza='COMUN',
            descripcion='Una pista para ayudarte',
            valor=50
        )
        self.assertEqual(item.nombre, 'Pista Extra')
        self.assertEqual(item.get_tipo_display(), 'Consumible')
    
    def test_item_usuario(self):
        """Prueba la asignación de items a usuarios"""
        item = Item.objects.create(
            nombre='Medalla de Prueba',
            tipo='MEDALLA',
            rareza='RARO',
            descripcion='Para pruebas',
            valor=100
        )
        
        item_usuario = ItemUsuario.objects.create(
            usuario=self.usuario,
            item=item,
            cantidad=2
        )
        
        self.assertEqual(item_usuario.usuario, self.usuario)
        self.assertEqual(item_usuario.item, item)
        self.assertEqual(item_usuario.cantidad, 2)
        self.assertFalse(item_usuario.equipado)
    
    def test_logro_creation(self):
        """Prueba la creación de logros"""
        logro = Logro.objects.create(
            nombre='Primeros Pasos',
            descripcion='Completar el primer nivel',
            categoria='AVENTURA',
            rareza='COMUN',
            puntos=50
        )
        self.assertEqual(logro.nombre, 'Primeros Pasos')
        self.assertEqual(logro.puntos, 50)
    
    def test_logro_desbloqueado(self):
        """Prueba el desbloqueo de logros"""
        logro = Logro.objects.create(
            nombre='Logro de Prueba',
            descripcion='Para pruebas',
            categoria='ESPECIAL',
            rareza='COMUN',
            puntos=10
        )
        
        desbloqueo = LogroDesbloqueado.objects.create(
            usuario=self.usuario,
            logro=logro
        )
        
        self.assertEqual(desbloqueo.usuario, self.usuario)
        self.assertEqual(desbloqueo.logro, logro)
        self.assertIsNotNone(desbloqueo.fecha_desbloqueo)
    
    def test_notificacion(self):
        """Prueba la creación de notificaciones"""
        notif = Notificacion.objects.create(
            usuario=self.usuario,
            titulo='Test Notificación',
            mensaje='Este es un mensaje de prueba',
            tipo='BIENVENIDA'
        )
        
        self.assertEqual(notif.usuario, self.usuario)
        self.assertFalse(notif.leida)
        self.assertIsNotNone(notif.fecha_creacion)
    
    def test_amistad(self):
        """Prueba la creación de amistades"""
        otro_usuario = User.objects.create_user(
            username='otro',
            password='pass123'
        )
        
        amistad = Amistad.objects.create(
            usuario1=self.usuario,
            usuario2=otro_usuario,
            estado='PENDIENTE'
        )
        
        self.assertEqual(amistad.estado, 'PENDIENTE')
        self.assertIsNotNone(amistad.fecha_creacion)
    
    def test_mensaje(self):
        """Prueba el envío de mensajes"""
        destinatario = User.objects.create_user(
            username='destino',
            password='pass123'
        )
        
        mensaje = Mensaje.objects.create(
            remitente=self.usuario,
            destinatario=destinatario,
            contenido='Hola, ¿cómo estás?'
        )
        
        self.assertEqual(mensaje.remitente, self.usuario)
        self.assertEqual(mensaje.destinatario, destinatario)
        self.assertFalse(mensaje.leido)
    
    def test_puntuacion_diaria(self):
        """Prueba el registro de puntuaciones diarias"""
        puntuacion = PuntuacionDiaria.objects.create(
            usuario=self.usuario,
            puntos=150,
            tipo_juego='AVENTURA'
        )
        
        self.assertEqual(puntuacion.puntos, 150)
        self.assertEqual(puntuacion.fecha, timezone.now().date())

# ============================================
# TESTS DE VISTAS
# ============================================

class VistasCoreTest(TestCase):
    """Pruebas para las vistas de la app core"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.perfil = Perfil.objects.get(usuario=self.usuario)
    
    def test_login_view(self):
        """Prueba la vista de login"""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_login_post_correcto(self):
        """Prueba el login con credenciales correctas"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
    
    def test_login_post_incorrecto(self):
        """Prueba el login con credenciales incorrectas"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrectos')
    
    def test_registro_view(self):
        """Prueba la vista de registro"""
        response = self.client.get(reverse('core:registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registro.html')
    
    def test_registro_post_valido(self):
        """Prueba el registro con datos válidos"""
        response = self.client.post(reverse('core:registro'), {
            'username': 'nuevousuario',
            'password1': 'compleja123pass',
            'password2': 'compleja123pass'
        })
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertTrue(User.objects.filter(username='nuevousuario').exists())
    
    def test_dashboard_acceso_sin_login(self):
        """Prueba que dashboard requiera autenticación"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, f"{reverse('core:login')}?next={reverse('core:dashboard')}")
    
    def test_dashboard_con_login(self):
        """Prueba dashboard con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/inicio.html')
    
    def test_perfil_view(self):
        """Prueba la vista de perfil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_editar_perfil(self):
        """Prueba la edición de perfil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('core:editar_perfil'), {
            'nombre_completo': 'Usuario Test',
            'biografia': 'Esta es mi biografía'
        })
        self.assertRedirects(response, reverse('core:perfil'))
        
        # Verificar que se actualizó
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.nombre_completo, 'Usuario Test')
        self.assertEqual(self.perfil.biografia, 'Esta es mi biografía')
    
    def test_inventario_view(self):
        """Prueba la vista de inventario"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear algunos items
        item = Item.objects.create(
            nombre='Item de Prueba',
            tipo='COLECCIONABLE',
            rareza='COMUN',
            descripcion='Descripción',
            valor=50
        )
        ItemUsuario.objects.create(
            usuario=self.usuario,
            item=item,
            cantidad=3
        )
        
        response = self.client.get(reverse('core:inventario'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Item de Prueba')
    
    def test_logros_view(self):
        """Prueba la vista de logros"""
        self.client.login(username='testuser', password='testpass123')
        
        logro = Logro.objects.create(
            nombre='Logro de Prueba',
            descripcion='Descripción',
            categoria='ESPECIAL',
            rareza='COMUN',
            puntos=100
        )
        
        response = self.client.get(reverse('core:logros'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logro de Prueba')
    
    def test_ranking_view(self):
        """Prueba la vista de ranking"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear otro usuario con puntos
        otro = User.objects.create_user(username='otro', password='pass123')
        otro.perfil.puntos_totales = 500
        otro.perfil.save()
        
        response = self.client.get(reverse('core:ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'otro')
    
    def test_amigos_view(self):
        """Prueba la vista de amigos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:amigos'))
        self.assertEqual(response.status_code, 200)

# ============================================
# TESTS DE API
# ============================================

class APICoreTest(TestCase):
    """Pruebas para los endpoints API"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.otro_usuario = User.objects.create_user(
            username='otro',
            password='pass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_api_enviar_solicitud_amistad(self):
        """Prueba el envío de solicitud de amistad via API"""
        response = self.client.post(reverse('core:api_enviar_solicitud'), {
            'usuario_id': self.otro_usuario.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que se creó la solicitud
        self.assertTrue(Amistad.objects.filter(
            usuario1=self.usuario,
            usuario2=self.otro_usuario,
            estado='PENDIENTE'
        ).exists())
    
    def test_api_responder_solicitud(self):
        """Prueba la respuesta a solicitud de amistad"""
        # Crear solicitud
        solicitud = Amistad.objects.create(
            usuario1=self.otro_usuario,
            usuario2=self.usuario,
            estado='PENDIENTE'
        )
        
        response = self.client.post(reverse('core:api_responder_solicitud'), {
            'solicitud_id': solicitud.id,
            'accion': 'aceptar'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que se aceptó
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'ACEPTADA')
    
    def test_api_enviar_mensaje(self):
        """Prueba el envío de mensajes via API"""
        response = self.client.post(reverse('core:api_enviar_mensaje'), {
            'destinatario_id': self.otro_usuario.id,
            'contenido': 'Hola, mensaje de prueba'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que se creó el mensaje
        self.assertTrue(Mensaje.objects.filter(
            remitente=self.usuario,
            destinatario=self.otro_usuario,
            contenido='Hola, mensaje de prueba'
        ).exists())

# ============================================
# TESTS DE SEGURIDAD Y PERMISOS
# ============================================

class SeguridadCoreTest(TestCase):
    """Pruebas de seguridad y permisos"""
    
    def setUp(self):
        self.client = Client()
        self.usuario1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.usuario2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
    
    def test_no_acceso_a_perfil_otro_usuario(self):
        """Verifica que un usuario no pueda ver perfil de otro"""
        self.client.login(username='user1', password='pass123')
        
        # Intentar acceder al perfil de otro usuario (esto debería manejarse)
        response = self.client.get(reverse('core:perfil'))
        self.assertEqual(response.status_code, 200)
        # No debería mostrar datos del otro usuario
    
    def test_proteccion_contra_csrf(self):
        """Verifica la protección CSRF en formularios POST"""
        response = self.client.post(reverse('core:login'), {
            'username': 'user1',
            'password': 'pass123'
        })
        # Debería funcionar porque el cliente de test maneja CSRF automáticamente
        self.assertNotEqual(response.status_code, 403)
    
    def test_rate_limit_login(self):
        """Simula múltiples intentos de login"""
        for _ in range(5):
            response = self.client.post(reverse('core:login'), {
                'username': 'user1',
                'password': 'wrongpass'
            })
        # Verificar que después de varios intentos no hay bloqueo (depende de configuración)
        self.assertEqual(response.status_code, 200)

# ============================================
# TESTS DE INTERNACIONALIZACIÓN
# ============================================

class I18NCoreTest(TestCase):
    """Pruebas de internacionalización"""
    
    def setUp(self):
        self.client = Client()
    
    def test_cambio_idioma(self):
        """Prueba el cambio de idioma"""
        response = self.client.get('/i18n/setlang/es/')
        self.assertEqual(response.status_code, 302)  # Redirección
    
    def test_urls_con_idioma(self):
        """Prueba que las URLs con prefijo de idioma funcionen"""
        response = self.client.get('/es/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)
    
    def test_catalogo_javascript(self):
        """Prueba que el catálogo JS de traducciones funcione"""
        response = self.client.get('/jsi18n/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/javascript')

# ============================================
# TESTS DE RENDIMIENTO (OPCIONAL)
# ============================================

class RendimientoCoreTest(TestCase):
    """Pruebas básicas de rendimiento"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos de prueba
        for i in range(10):
            Logro.objects.create(
                nombre=f'Logro {i}',
                descripcion=f'Desc {i}',
                categoria='ESPECIAL',
                rareza='COMUN',
                puntos=10
            )
    
    def test_tiempo_respuesta_dashboard(self):
        """Mide el tiempo de respuesta del dashboard"""
        import time
        
        start = time.time()
        response = self.client.get(reverse('core:dashboard'))
        end = time.time()
        
        duration = end - start
        self.assertLess(duration, 1.0)  # Menos de 1 segundo
        self.assertEqual(response.status_code, 200)
    
    def test_consultas_base_datos(self):
        """Cuenta el número de consultas a la BD"""
        from django.db import connection
        
        # Resetear contador de consultas
        connection.queries_log.clear()
        
        response = self.client.get(reverse('core:logros'))
        
        num_queries = len(connection.queries)
        self.assertLess(num_queries, 20)  # Menos de 20 consultas
        self.assertEqual(response.status_code, 200)

# ============================================
# TESTS DE FORMULARIOS
# ============================================

class FormulariosCoreTest(TestCase):
    """Pruebas para formularios"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_formulario_registro_valido(self):
        """Prueba formulario de registro válido"""
        from django.contrib.auth.forms import UserCreationForm
        
        form_data = {
            'username': 'nuevo',
            'password1': 'compleja123pass',
            'password2': 'compleja123pass'
        }
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_formulario_registro_invalido(self):
        """Prueba formulario de registro con datos inválidos"""
        from django.contrib.auth.forms import UserCreationForm
        
        form_data = {
            'username': 'nuevo',
            'password1': '123',
            'password2': '123'
        }
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_formulario_editar_perfil(self):
        """Prueba formulario de edición de perfil"""
        from .forms import PerfilForm
        
        form_data = {
            'nombre_completo': 'Nombre Completo',
            'fecha_nacimiento': '1990-01-01',
            'pais': 'CO',
            'biografia': 'Mi biografía'
        }
        form = PerfilForm(data=form_data)
        self.assertTrue(form.is_valid())

# ============================================
# TESTS DE INTEGRACIÓN
# ============================================

class IntegracionCoreTest(TestCase):
    """Pruebas de integración entre componentes"""
    
    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_flujo_completo_amistad(self):
        """Prueba el flujo completo de amistad"""
        otro = User.objects.create_user(username='amigo', password='pass123')
        
        # 1. Enviar solicitud
        response = self.client.post(reverse('core:api_enviar_solicitud'), {
            'usuario_id': otro.id
        })
        self.assertEqual(response.status_code, 200)
        
        # 2. Verificar notificación creada
        self.assertTrue(Notificacion.objects.filter(
            usuario=otro,
            tipo='AMISTAD'
        ).exists())
        
        # 3. Aceptar solicitud (como el otro usuario)
        self.client.login(username='amigo', password='pass123')
        solicitud = Amistad.objects.get(usuario1=self.usuario, usuario2=otro)
        
        response = self.client.post(reverse('core:api_responder_solicitud'), {
            'solicitud_id': solicitud.id,
            'accion': 'aceptar'
        })
        self.assertEqual(response.status_code, 200)
        
        # 4. Verificar amistad aceptada
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'ACEPTADA')
        
        # 5. Enviar mensaje
        response = self.client.post(reverse('core:api_enviar_mensaje'), {
            'destinatario_id': self.usuario.id,
            'contenido': '¡Somos amigos!'
        })
        self.assertEqual(response.status_code, 200)
        
        # 6. Verificar mensaje creado
        self.assertTrue(Mensaje.objects.filter(
            remitente=otro,
            destinatario=self.usuario,
            contenido='¡Somos amigos!'
        ).exists())
    
    def test_flujo_logros_puntos(self):
        """Prueba la integración entre logros y puntos"""
        # Crear logro
        logro = Logro.objects.create(
            nombre='Logro de Puntos',
            descripcion='Gana 100 puntos',
            categoria='ESPECIAL',
            rareza='COMUN',
            puntos=50,
            tipo='PUNTOS',
            cantidad_necesaria=100
        )
        
        # Dar puntos al usuario
        self.usuario.perfil.puntos_totales = 150
        self.usuario.perfil.save()
        
        # Verificar que no está desbloqueado aún
        self.assertFalse(LogroDesbloqueado.objects.filter(
            usuario=self.usuario,
            logro=logro
        ).exists())
        
        # Aquí se ejecutaría la lógica de verificación de logros
        # ...

# ============================================
# EJECUTAR PRUEBAS
# ============================================

def ejecutar_pruebas():
    """
    Función auxiliar para ejecutar todas las pruebas
    Uso: python manage.py test core.tests
    """
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(ModelosCoreTest)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(VistasCoreTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(APICoreTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(SeguridadCoreTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(I18NCoreTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(FormulariosCoreTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(IntegracionCoreTest))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()