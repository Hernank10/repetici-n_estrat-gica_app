from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q, F
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from datetime import timedelta, datetime
from .models import (
    User, Perfil, Inventario, Item, ItemUsuario, Logro, LogroDesbloqueado,
    AventuraNivel, ProgresoAventura, PreguntaOrtografia, ProgresoOrtografia,
    PuntuacionDiaria, Notificacion, Amistad, Mensaje
)

# ============================================
# DECORADOR PERSONALIZADO
# ============================================

def verificar_perfil_completo(view_func):
    """Decorador para verificar que el perfil esté completo"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            perfil = request.user.perfil
            if not perfil.nombre_completo or not perfil.fecha_nacimiento:
                messages.warning(request, 'Por favor completa tu perfil antes de continuar')
                return redirect('juegos:editar_perfil')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

def registro_view(request):
    """Registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('juegos:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil automáticamente
            Perfil.objects.create(
                usuario=user,
                fecha_registro=timezone.now()
            )
            
            # Crear inventario
            Inventario.objects.create(usuario=user)
            
            # Items iniciales
            item_bienvenida = Item.objects.get_or_create(
                nombre='Kit de Bienvenida',
                defaults={
                    'tipo': 'ESPECIAL',
                    'rareza': 'COMUN',
                    'icono': 'gift',
                    'descripcion': 'Item de bienvenida para nuevos estudiantes',
                    'valor': 100
                }
            )[0]
            
            ItemUsuario.objects.create(
                usuario=user,
                item=item_bienvenida,
                fecha_obtencion=timezone.now()
            )
            
            # Login automático
            login(request, user)
            messages.success(request, f'¡Bienvenido a la Academia, {user.username}!')
            
            # Notificación de bienvenida
            Notificacion.objects.create(
                usuario=user,
                titulo='¡Bienvenido!',
                mensaje='Completa tu perfil y empieza a jugar',
                tipo='BIENVENIDA'
            )
            
            return redirect('juegos:editar_perfil')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registro.html', {
        'form': form,
        'titulo': 'Registro',
        'beneficios': [
            {'icono': 'gamepad', 'texto': 'Juegos educativos'},
            {'icono': 'trophy', 'texto': 'Logros y recompensas'},
            {'icono': 'chart-line', 'texto': 'Sigue tu progreso'},
            {'icono': 'users', 'texto': 'Compite con amigos'},
        ]
    })

def login_view(request):
    """Inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('juegos:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Actualizar última conexión
            perfil = user.perfil
            perfil.ultima_conexion = timezone.now()
            perfil.save()
            
            # Verificar racha
            verificar_racha(user)
            
            messages.success(request, f'¡Hola de nuevo, {user.username}!')
            
            # Redireccionar a la página solicitada
            next_url = request.GET.get('next', 'juegos:dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'titulo': 'Iniciar Sesión'
    })

def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, '¡Hasta pronto!')
    return redirect('juegos:login')

# ============================================
# VISTAS DE PERFIL
# ============================================

@login_required
def perfil_view(request):
    """Vista del perfil del usuario"""
    perfil = request.user.perfil
    context = obtener_contexto_perfil(request.user)
    
    return render(request, 'juegos/perfil/perfil.html', context)

@login_required
def editar_perfil_view(request):
    """Editar perfil del usuario"""
    perfil = request.user.perfil
    
    if request.method == 'POST':
        # Actualizar datos del perfil
        perfil.nombre_completo = request.POST.get('nombre_completo', '')
        perfil.fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
        perfil.pais = request.POST.get('pais', '')
        perfil.biografia = request.POST.get('biografia', '')
        perfil.avatar = request.FILES.get('avatar', perfil.avatar)
        perfil.save()
        
        # Actualizar email del usuario
        email = request.POST.get('email')
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()
        
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('juegos:perfil')
    
    context = {
        'titulo': 'Editar Perfil',
        'perfil': perfil,
        'paises': obtener_lista_paises(),
    }
    
    return render(request, 'juegos/perfil/editar.html', context)

@login_required
def inventario_view(request):
    """Vista del inventario del usuario"""
    inventario = request.user.inventario
    items_usuario = ItemUsuario.objects.filter(usuario=request.user).select_related('item')
    
    # Agrupar por categoría
    items_por_categoria = {
        'todos': items_usuario,
        'especiales': items_usuario.filter(item__tipo='ESPECIAL'),
        'consumibles': items_usuario.filter(item__tipo='CONSUMIBLE'),
        'coleccionables': items_usuario.filter(item__tipo='COLECCIONABLE'),
        'medallas': items_usuario.filter(item__tipo='MEDALLA'),
    }
    
    # Estadísticas del inventario
    stats = {
        'total_items': items_usuario.count(),
        'items_equipados': items_usuario.filter(equipado=True).count(),
        'valor_total': sum(item.item.valor * item.cantidad for item in items_usuario),
        'rareza_maxima': obtener_rareza_maxima(items_usuario),
    }
    
    # Progreso de colección
    total_coleccionables = Item.objects.filter(tipo='COLECCIONABLE').count()
    coleccionables_obtenidos = items_usuario.filter(item__tipo='COLECCIONABLE').count()
    
    stats_coleccion = {
        'total': total_coleccionables,
        'obtenidos': coleccionables_obtenidos,
        'porcentaje': (coleccionables_obtenidos / total_coleccionables * 100) if total_coleccionables > 0 else 0
    }
    
    context = {
        'titulo': 'Mi Inventario',
        'inventario': inventario,
        'items_por_categoria': items_por_categoria,
        'stats': stats,
        'stats_coleccion': stats_coleccion,
    }
    
    return render(request, 'juegos/perfil/inventario.html', context)

# ============================================
# VISTAS DE LOGROS
# ============================================

@login_required
def logros_view(request):
    """Galería de logros"""
    todos_logros = Logro.objects.all().order_by('categoria', 'dificultad')
    logros_usuario = LogroDesbloqueado.objects.filter(
        usuario=request.user
    ).select_related('logro')
    
    logros_ids = [l.logro.id for l in logros_usuario]
    
    # Organizar por categoría
    categorias = {}
    for logro in todos_logros:
        if logro.categoria not in categorias:
            categorias[logro.categoria] = {
                'nombre': logro.get_categoria_display(),
                'icono': obtener_icono_categoria(logro.categoria),
                'logros': [],
                'total': 0,
                'obtenidos': 0
            }
        
        desbloqueado = logro.id in logros_ids
        progreso = calcular_progreso_logro(request.user, logro) if not desbloqueado else None
        
        categorias[logro.categoria]['logros'].append({
            'logro': logro,
            'desbloqueado': desbloqueado,
            'fecha': next((l.fecha_desbloqueo for l in logros_usuario if l.logro.id == logro.id), None),
            'progreso': progreso,
        })
        
        categorias[logro.categoria]['total'] += 1
        if desbloqueado:
            categorias[logro.categoria]['obtenidos'] += 1
    
    # Logros recientes
    recientes = logros_usuario.order_by('-fecha_desbloqueo')[:5]
    
    # Próximos logros (más cercanos a desbloquear)
    proximos = calcular_proximos_logros(request.user, todos_logros, logros_ids)
    
    # Estadísticas por rareza
    rarezas = calcular_stats_rareza(request.user, todos_logros)
    
    context = {
        'titulo': 'Mis Logros',
        'categorias': categorias.values(),
        'recientes': recientes,
        'proximos': proximos[:5],
        'rarezas': rarezas,
        'total_logros': todos_logros.count(),
        'logros_obtenidos': len(logros_ids),
        'progreso_total': (len(logros_ids) / todos_logros.count() * 100) if todos_logros.count() > 0 else 0,
    }
    
    return render(request, 'juegos/logros/galeria.html', context)

# ============================================
# VISTAS DE RANKING
# ============================================

@login_required
def ranking_view(request):
    """Vista principal del ranking"""
    # Obtener filtros
    periodo = request.GET.get('periodo', 'total')
    juego = request.GET.get('juego', 'todos')
    
    # Obtener rankings
    rankings = obtener_ranking_completo(request.user, periodo, juego)
    
    # Posición del usuario
    posicion_usuario = next(
        (item for item in rankings if item['usuario']['id'] == request.user.id),
        None
    )
    
    # Estadísticas globales
    stats_globales = obtener_stats_globales_ranking()
    
    # Top 3
    top_3 = rankings[:3] if rankings else []
    
    # Logros de ranking del usuario
    logros_ranking = obtener_logros_ranking_usuario(request.user)
    
    context = {
        'titulo': 'Ranking de la Academia',
        'rankings': rankings,
        'posicion_usuario': posicion_usuario,
        'stats_globales': stats_globales,
        'top_3': top_3,
        'logros_ranking': logros_ranking,
        'filtros': {
            'periodo': periodo,
            'juego': juego,
        }
    }
    
    return render(request, 'juegos/ranking/leaderboard.html', context)

@login_required
def ranking_detalle_view(request, usuario_id):
    """Vista detallada de un usuario en el ranking"""
    usuario = get_object_or_404(User, id=usuario_id)
    perfil = usuario.perfil
    
    # Estadísticas detalladas
    stats = {
        'puntos_totales': perfil.puntos_totales,
        'nivel_maestria': perfil.nivel_maestria,
        'logros': LogroDesbloqueado.objects.filter(usuario=usuario).count(),
        'racha_actual': perfil.racha_actual,
        'racha_maxima': perfil.racha_maxima,
        'dias_activos': calcular_dias_activos(usuario),
        'miembro_desde': usuario.date_joined,
    }
    
    # Progreso en juegos
    progreso_aventura = ProgresoAventura.objects.filter(usuario=usuario).aggregate(
        niveles_completados=Count('id', filter=Q(completado=True)),
        puntuacion_total=Sum('puntuacion'),
        tiempo_total=Sum('tiempo_jugado')
    )
    
    progreso_ortografia = ProgresoOrtografia.objects.filter(usuario=usuario).aggregate(
        partidas=Count('id'),
        aciertos=Sum('aciertos'),
        errores=Sum('errores')
    )
    
    # Posiciones en diferentes rankings
    posiciones = {
        'global': obtener_posicion_usuario(usuario, 'total', 'todos'),
        'semanal': obtener_posicion_usuario(usuario, 'semanal', 'todos'),
        'aventura': obtener_posicion_usuario(usuario, 'total', 'aventura'),
        'ortografia': obtener_posicion_usuario(usuario, 'total', 'ortografia'),
    }
    
    # Actividad reciente
    actividades = obtener_actividad_recente_usuario(usuario)
    
    # Verificar si son amigos
    son_amigos = Amistad.objects.filter(
        (Q(usuario1=request.user) & Q(usuario2=usuario)) |
        (Q(usuario1=usuario) & Q(usuario2=request.user)),
        estado='ACEPTADA'
    ).exists()
    
    context = {
        'titulo': f'Perfil de {usuario.username}',
        'usuario_perfil': usuario,
        'perfil': perfil,
        'stats': stats,
        'progreso_aventura': progreso_aventura,
        'progreso_ortografia': progreso_ortografia,
        'posiciones': posiciones,
        'actividades': actividades,
        'son_amigos': son_amigos,
        'solicitud_pendiente': tiene_solicitud_pendiente(request.user, usuario),
    }
    
    return render(request, 'juegos/ranking/detalle_usuario.html', context)

# ============================================
# VISTAS DE AMISTAD Y SOCIAL
# ============================================

@login_required
def amigos_view(request):
    """Vista de amigos y solicitudes"""
    # Amigos aceptados
    amigos = Amistad.objects.filter(
        (Q(usuario1=request.user) | Q(usuario2=request.user)),
        estado='ACEPTADA'
    ).select_related('usuario1', 'usuario2')
    
    lista_amigos = []
    for amistad in amigos:
        amigo = amistad.usuario2 if amistad.usuario1 == request.user else amistad.usuario1
        lista_amigos.append({
            'usuario': amigo,
            'fecha_amistad': amistad.fecha_actualizacion,
            'en_linea': esta_en_linea(amigo),
        })
    
    # Solicitudes pendientes recibidas
    solicitudes_recibidas = Amistad.objects.filter(
        usuario2=request.user,
        estado='PENDIENTE'
    ).select_related('usuario1')
    
    # Solicitudes enviadas pendientes
    solicitudes_enviadas = Amistad.objects.filter(
        usuario1=request.user,
        estado='PENDIENTE'
    ).select_related('usuario2')
    
    # Sugerencias de amigos (usuarios con intereses similares)
    sugerencias = obtener_sugerencias_amigos(request.user)
    
    context = {
        'titulo': 'Mis Amigos',
        'amigos': lista_amigos,
        'solicitudes_recibidas': solicitudes_recibidas,
        'solicitudes_enviadas': solicitudes_enviadas,
        'sugerencias': sugerencias,
    }
    
    return render(request, 'juegos/social/amigos.html', context)

@login_required
def mensajes_view(request):
    """Vista de mensajes privados"""
    conversaciones = obtener_conversaciones(request.user)
    
    context = {
        'titulo': 'Mensajes',
        'conversaciones': conversaciones,
    }
    
    return render(request, 'juegos/social/mensajes.html', context)

@login_required
def conversacion_view(request, usuario_id):
    """Vista de una conversación específica"""
    otro_usuario = get_object_or_404(User, id=usuario_id)
    
    # Marcar mensajes como leídos
    Mensaje.objects.filter(
        remitente=otro_usuario,
        destinatario=request.user,
        leido=False
    ).update(leido=True)
    
    # Obtener mensajes
    mensajes = Mensaje.objects.filter(
        (Q(remitente=request.user) & Q(destinatario=otro_usuario)) |
        (Q(remitente=otro_usuario) & Q(destinatario=request.user))
    ).order_by('fecha_envio')
    
    context = {
        'titulo': f'Chat con {otro_usuario.username}',
        'otro_usuario': otro_usuario,
        'mensajes': mensajes,
    }
    
    return render(request, 'juegos/social/conversacion.html', context)

# ============================================
# VISTAS DE NOTIFICACIONES
# ============================================

@login_required
def notificaciones_view(request):
    """Centro de notificaciones"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    # Marcar todas como leídas
    notificaciones.filter(leida=False).update(leida=True)
    
    # Agrupar por fecha
    notificaciones_agrupadas = agrupar_notificaciones(notificaciones)
    
    context = {
        'titulo': 'Notificaciones',
        'notificaciones_agrupadas': notificaciones_agrupadas,
        'no_leidas': 0,
    }
    
    return render(request, 'juegos/social/notificaciones.html', context)

# ============================================
# VISTAS DE CONFIGURACIÓN
# ============================================

@login_required
def configuracion_view(request):
    """Configuración de la cuenta"""
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'cambiar_password':
            # Cambiar contraseña
            password_actual = request.POST.get('password_actual')
            password_nueva = request.POST.get('password_nueva')
            
            if request.user.check_password(password_actual):
                request.user.set_password(password_nueva)
                request.user.save()
                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('juegos:login')
            else:
                messages.error(request, 'Contraseña actual incorrecta')
        
        elif accion == 'cambiar_email':
            # Cambiar email
            nuevo_email = request.POST.get('email')
            request.user.email = nuevo_email
            request.user.save()
            messages.success(request, 'Email actualizado correctamente')
        
        elif accion == 'preferencias':
            # Actualizar preferencias
            perfil = request.user.perfil
            perfil.preferencias = request.POST.get('preferencias', '{}')
            perfil.notificaciones_email = request.POST.get('notificaciones_email') == 'on'
            perfil.privacidad_perfil = request.POST.get('privacidad_perfil', 'PUBLICO')
            perfil.save()
            messages.success(request, 'Preferencias actualizadas')
    
    context = {
        'titulo': 'Configuración',
        'usuario': request.user,
        'perfil': request.user.perfil,
    }
    
    return render(request, 'juegos/configuracion/config.html', context)

# ============================================
# VISTAS DE JUEGOS
# ============================================

@login_required
@verificar_perfil_completo
def aventura_list_view(request):
    """Lista de niveles de aventura"""
    niveles = AventuraNivel.objects.all().order_by('orden')
    progresos = ProgresoAventura.objects.filter(usuario=request.user)
    
    # Procesar cada nivel
    for nivel in niveles:
        progreso = progresos.filter(nivel=nivel).first()
        nivel.completado = progreso and progreso.completado
        nivel.puntuacion_obtenida = progreso.puntuacion if progreso else 0
        nivel.mejor_tiempo = progreso.tiempo_jugado if progreso else None
        
        # Determinar si está bloqueado
        if nivel.orden > 1:
            nivel_anterior = niveles.get(orden=nivel.orden - 1)
            nivel_anterior_completado = progresos.filter(
                nivel=nivel_anterior, completado=True
            ).exists()
            nivel.bloqueado = not nivel_anterior_completado
        else:
            nivel.bloqueado = False
    
    # Estadísticas generales
    stats = {
        'niveles_completados': progresos.filter(completado=True).count(),
        'puntuacion_total': progresos.aggregate(total=Sum('puntuacion'))['total'] or 0,
        'tiempo_total': progresos.aggregate(total=Sum('tiempo_jugado'))['total'] or timedelta(),
    }
    
    context = {
        'titulo': 'Aventura Educativa',
        'niveles': niveles,
        'stats': stats,
    }
    
    return render(request, 'juegos/aventura/lista_niveles.html', context)

@login_required
@verificar_perfil_completo
def aventura_jugar_view(request, nivel_id):
    """Jugar un nivel de aventura"""
    nivel = get_object_or_404(AventuraNivel, id=nivel_id)
    
    # Verificar si está desbloqueado
    if not nivel_esta_desbloqueado(request.user, nivel):
        messages.warning(request, 'Completa el nivel anterior primero')
        return redirect('juegos:aventura_list')
    
    # Obtener preguntas del nivel
    preguntas = nivel.preguntas.all()
    
    # Convertir a JSON para JavaScript
    preguntas_json = []
    for p in preguntas:
        preguntas_json.append({
            'id': p.id,
            'texto': p.texto,
            'opciones': p.opciones,
            'correcta': p.respuesta_correcta,
            'pista': p.pista,
            'puntos': p.puntos,
        })
    
    # Ayudas disponibles del inventario
    ayudas = obtener_ayudas_disponibles(request.user)
    
    context = {
        'titulo': f'Nivel {nivel.nivel}: {nivel.titulo}',
        'nivel': nivel,
        'preguntas_json': preguntas_json,
        'ayudas': ayudas,
        'tiempo_limite': nivel.tiempo_limite,
    }
    
    return render(request, 'juegos/aventura/jugar_nivel.html', context)

@login_required
@verificar_perfil_completo
def ortografia_categorias_view(request):
    """Categorías de ortografía"""
    categorias = PreguntaOrtografia.objects.values('categoria').annotate(
        total=Count('id')
    ).order_by('categoria')
    
    # Estadísticas por categoría
    for cat in categorias:
        progreso = ProgresoOrtografia.objects.filter(
            usuario=request.user,
            categoria=cat['categoria']
        ).aggregate(
            aciertos=Sum('aciertos'),
            errores=Sum('errores'),
            partidas=Count('id')
        )
        
        cat['aciertos'] = progreso['aciertos'] or 0
        cat['errores'] = progreso['errores'] or 0
        cat['partidas'] = progreso['partidas'] or 0
        
        total = cat['aciertos'] + cat['errores']
        cat['precision'] = round((cat['aciertos'] / total * 100), 1) if total > 0 else 0
    
    # Estadísticas generales
    stats = ProgresoOrtografia.objects.filter(usuario=request.user).aggregate(
        total_partidas=Count('id'),
        total_aciertos=Sum('aciertos'),
        total_errores=Sum('errores')
    )
    
    total_preguntas = (stats['total_aciertos'] or 0) + (stats['total_errores'] or 0)
    stats['precision_global'] = round((stats['total_aciertos'] or 0) / total_preguntas * 100, 1) if total_preguntas > 0 else 0
    
    context = {
        'titulo': 'Desafío de Ortografía',
        'categorias': categorias,
        'stats': stats,
    }
    
    return render(request, 'juegos/ortografia/categorias.html', context)

@login_required
@verificar_perfil_completo
def ortografia_jugar_view(request, categoria=None):
    """Jugar ortografía"""
    if categoria:
        preguntas = PreguntaOrtografia.objects.filter(categoria=categoria)
        titulo = f'Ortografía - {categoria.title()}'
    else:
        preguntas = PreguntaOrtografia.objects.all().order_by('?')[:20]
        titulo = 'Ortografía - Práctica General'
    
    # Convertir a JSON
    preguntas_json = []
    for p in preguntas:
        preguntas_json.append({
            'id': p.id,
            'palabra': p.palabra,
            'opciones': p.opciones,
            'correcta': p.palabra_correcta,
            'categoria': p.categoria,
            'dificultad': p.dificultad,
        })
    
    context = {
        'titulo': titulo,
        'preguntas_json': preguntas_json,
        'categoria_actual': categoria,
        'total_preguntas': preguntas.count(),
    }
    
    return render(request, 'juegos/ortografia/jugar_partida.html', context)

# ============================================
# API ENDPOINTS
# ============================================

@login_required
@require_POST
def api_guardar_progreso_aventura(request):
    """Guardar progreso de aventura"""
    try:
        nivel_id = request.POST.get('nivel_id')
        puntuacion = int(request.POST.get('puntuacion', 0))
        tiempo = int(request.POST.get('tiempo', 0))
        completado = request.POST.get('completado') == 'true'
        
        nivel = AventuraNivel.objects.get(id=nivel_id)
        
        # Guardar o actualizar progreso
        progreso, created = ProgresoAventura.objects.update_or_create(
            usuario=request.user,
            nivel=nivel,
            defaults={
                'puntuacion': puntuacion,
                'tiempo_jugado': timedelta(seconds=tiempo),
                'completado': completado,
                'fecha_completado': timezone.now() if completado else None,
            }
        )
        
        # Actualizar puntos totales del perfil
        if completado:
            perfil = request.user.perfil
            perfil.puntos_totales += puntuacion
            perfil.save()
            
            # Registrar puntuación diaria
            PuntuacionDiaria.objects.create(
                usuario=request.user,
                puntos=puntuacion,
                tipo_juego='AVENTURA',
                fecha=timezone.now().date()
            )
            
            # Verificar logros
            verificar_logros_aventura(request.user)
        
        return JsonResponse({
            'success': True,
            'puntuacion_total': request.user.perfil.puntos_totales,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def api_guardar_progreso_ortografia(request):
    """Guardar progreso de ortografía"""
    try:
        categoria = request.POST.get('categoria', 'general')
        aciertos = int(request.POST.get('aciertos', 0))
        errores = int(request.POST.get('errores', 0))
        tiempo = int(request.POST.get('tiempo', 0))
        
        # Guardar progreso
        progreso = ProgresoOrtografia.objects.create(
            usuario=request.user,
            categoria=categoria,
            aciertos=aciertos,
            errores=errores,
            tiempo_jugado=timedelta(seconds=tiempo),
            fecha=timezone.now()
        )
        
        # Calcular puntos (10 por acierto, -5 por error)
        puntos = (aciertos * 10) - (errores * 5)
        
        # Actualizar perfil
        perfil = request.user.perfil
        perfil.puntos_totales += max(0, puntos)
        perfil.save()
        
        # Registrar puntuación diaria
        PuntuacionDiaria.objects.create(
            usuario=request.user,
            puntos=max(0, puntos),
            tipo_juego='ORTOGRAFIA',
            fecha=timezone.now().date()
        )
        
        # Verificar logros
        verificar_logros_ortografia(request.user)
        
        return JsonResponse({
            'success': True,
            'puntos_ganados': max(0, puntos),
            'puntuacion_total': perfil.puntos_totales,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def api_usar_item(request):
    """Usar un item del inventario"""
    try:
        item_usuario_id = request.POST.get('item_id')
        item_usuario = ItemUsuario.objects.get(id=item_usuario_id, usuario=request.user)
        
        # Verificar si es consumible
        if item_usuario.item.tipo == 'CONSUMIBLE':
            # Aplicar efecto del item
            efecto = aplicar_efecto_item(request.user, item_usuario.item)
            
            # Reducir cantidad o eliminar
            if item_usuario.cantidad > 1:
                item_usuario.cantidad -= 1
                item_usuario.save()
            else:
                item_usuario.delete()
            
            return JsonResponse({
                'success': True,
                'efecto': efecto,
                'mensaje': f'Has usado {item_usuario.item.nombre}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Este item no es consumible'
            })
            
    except ItemUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item no encontrado'})

@login_required
@require_POST
def api_equipar_item(request):
    """Equipar o desequipar un item"""
    try:
        item_usuario_id = request.POST.get('item_id')
        accion = request.POST.get('accion', 'equipar')
        
        item_usuario = ItemUsuario.objects.get(id=item_usuario_id, usuario=request.user)
        
        if accion == 'equipar':
            # Desequipar otros items del mismo tipo
            ItemUsuario.objects.filter(
                usuario=request.user,
                item__tipo=item_usuario.item.tipo,
                equipado=True
            ).update(equipado=False)
            
            item_usuario.equipado = True
            item_usuario.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'{item_usuario.item.nombre} equipado'
            })
            
        else:  # desequipar
            item_usuario.equipado = False
            item_usuario.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': f'{item_usuario.item.nombre} desequipado'
            })
            
    except ItemUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item no encontrado'})

@login_required
@require_POST
def api_enviar_solicitud_amistad(request):
    """Enviar solicitud de amistad"""
    try:
        usuario_id = request.POST.get('usuario_id')
        usuario_destino = User.objects.get(id=usuario_id)
        
        if usuario_destino == request.user:
            return JsonResponse({'success': False, 'error': 'No puedes enviarte solicitud a ti mismo'})
        
        # Verificar si ya existe
        amistad_existente = Amistad.objects.filter(
            (Q(usuario1=request.user) & Q(usuario2=usuario_destino)) |
            (Q(usuario1=usuario_destino) & Q(usuario2=request.user))
        ).first()
        
        if amistad_existente:
            if amistad_existente.estado == 'ACEPTADA':
                return JsonResponse({'success': False, 'error': 'Ya son amigos'})
            elif amistad_existente.estado == 'PENDIENTE':
                return JsonResponse({'success': False, 'error': 'Solicitud ya enviada'})
        
        # Crear solicitud
        Amistad.objects.create(
            usuario1=request.user,
            usuario2=usuario_destino,
            estado='PENDIENTE'
        )
        
        # Crear notificación
        Notificacion.objects.create(
            usuario=usuario_destino,
            titulo='Solicitud de amistad',
            mensaje=f'{request.user.username} quiere ser tu amigo',
            tipo='AMISTAD'
        )
        
        return JsonResponse({'success': True, 'mensaje': 'Solicitud enviada'})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})

@login_required
@require_POST
def api_responder_solicitud(request):
    """Aceptar o rechazar solicitud de amistad"""
    try:
        solicitud_id = request.POST.get('solicitud_id')
        accion = request.POST.get('accion')  # aceptar o rechazar
        
        solicitud = Amistad.objects.get(
            id=solicitud_id,
            usuario2=request.user,
            estado='PENDIENTE'
        )
        
        if accion == 'aceptar':
            solicitud.estado = 'ACEPTADA'
            solicitud.save()
            
            # Notificación al otro usuario
            Notificacion.objects.create(
                usuario=solicitud.usuario1,
                titulo='Solicitud aceptada',
                mensaje=f'{request.user.username} aceptó tu solicitud de amistad',
                tipo='AMISTAD'
            )
            
            return JsonResponse({'success': True, 'mensaje': 'Amistad aceptada'})
            
        else:  # rechazar
            solicitud.delete()
            return JsonResponse({'success': True, 'mensaje': 'Solicitud rechazada'})
            
    except Amistad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Solicitud no encontrada'})

@login_required
@require_POST
def api_enviar_mensaje(request):
    """Enviar mensaje privado"""
    try:
        destinatario_id = request.POST.get('destinatario_id')
        contenido = request.POST.get('contenido')
        
        destinatario = User.objects.get(id=destinatario_id)
        
        mensaje = Mensaje.objects.create(
            remitente=request.user,
            destinatario=destinatario,
            contenido=contenido
        )
        
        # Notificación
        Notificacion.objects.create(
            usuario=destinatario,
            titulo='Nuevo mensaje',
            mensaje=f'{request.user.username} te envió un mensaje',
            tipo='MENSAJE'
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': {
                'id': mensaje.id,
                'contenido': mensaje.contenido,
                'fecha': mensaje.fecha_envio.strftime('%H:%M'),
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def obtener_contexto_perfil(user):
    """Obtiene todo el contexto para el perfil"""
    perfil = user.perfil
    
    # Estadísticas
    stats = {
        'puntos_totales': perfil.puntos_totales,
        'nivel_maestria': perfil.nivel_maestria,
        'racha_actual': perfil.racha_actual,
        'racha_maxima': perfil.racha_maxima,
        'ultima_conexion': perfil.ultima_conexion,
        'miembro_desde': user.date_joined,
    }
    
    # Progreso en juegos
    progreso_aventura = ProgresoAventura.objects.filter(usuario=user).aggregate(
        niveles_completados=Count('id', filter=Q(completado=True)),
        puntuacion_total=Sum('puntuacion'),
    )
    
    progreso_ortografia = ProgresoOrtografia.objects.filter(usuario=user).aggregate(
        aciertos=Sum('aciertos'),
        errores=Sum('errores'),
    )
    
    # Logros recientes
    logros_recientes = LogroDesbloqueado.objects.filter(
        usuario=user
    ).select_related('logro').order_by('-fecha_desbloqueo')[:5]
    
    # Actividad reciente
    actividad = obtener_actividad_usuario(user, limit=10)
    
    return {
        'perfil': perfil,
        'stats': stats,
        'progreso_aventura': progreso_aventura,
        'progreso_ortografia': progreso_ortografia,
        'logros_recientes': logros_recientes,
        'actividad': actividad,
    }

def verificar_racha(user):
    """Verifica y actualiza la racha del usuario"""
    perfil = user.perfil
    hoy = timezone.now().date()
    
    # Última actividad registrada
    ultima_actividad = PuntuacionDiaria.objects.filter(
        usuario=user
    ).order_by('-fecha').first()
    
    if ultima_actividad:
        diferencia = (hoy - ultima_actividad.fecha).days
        
        if diferencia == 1:
            # Día consecutivo
            perfil.racha_actual += 1
            if perfil.racha_actual > perfil.racha_maxima:
                perfil.racha_maxima = perfil.racha_actual
        elif diferencia > 1:
            # Se rompió la racha
            perfil.racha_actual = 1
    else:
        # Primera actividad
        perfil.racha_actual = 1
    
    perfil.save()

def obtener_ranking_completo(usuario_actual, periodo='total', juego='todos'):
    """Obtiene el ranking completo con todos los datos"""
    rankings = []
    fecha_inicio = obtener_fecha_inicio_ranking(periodo)
    
    # Obtener todos los usuarios con puntos
    if fecha_inicio:
        # Ranking por período
        puntuaciones = PuntuacionDiaria.objects.filter(
            fecha__gte=fecha_inicio
        ).values('usuario').annotate(
            total_puntos=Sum('puntos'),
            partidas=Count('id')
        ).order_by('-total_puntos')
        
        for idx, item in enumerate(puntuaciones[:100], 1):
            usuario = User.objects.get(id=item['usuario'])
            perfil = usuario.perfil
            
            rankings.append({
                'posicion': idx,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'avatar': usuario.username[0].upper(),
                    'nivel': perfil.nivel_maestria,
                },
                'puntos': item['total_puntos'],
                'partidas': item['partidas'],
                'racha': perfil.racha_actual,
                'ultima_actividad': perfil.ultima_conexion,
                'es_usuario_actual': usuario == usuario_actual,
            })
    else:
        # Ranking total
        usuarios = User.objects.filter(perfil__puntos_totales__gt=0).order_by('-perfil__puntos_totales')[:100]
        
        for idx, usuario in enumerate(usuarios, 1):
            perfil = usuario.perfil
            rankings.append({
                'posicion': idx,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'avatar': usuario.username[0].upper(),
                    'nivel': perfil.nivel_maestria,
                },
                'puntos': perfil.puntos_totales,
                'racha': perfil.racha_actual,
                'ultima_actividad': perfil.ultima_conexion,
                'es_usuario_actual': usuario == usuario_actual,
            })
    
    return rankings

def obtener_stats_globales_ranking():
    """Estadísticas globales para el ranking"""
    total_usuarios = User.objects.count()
    usuarios_activos_hoy = User.objects.filter(
        perfil__ultima_conexion__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    puntos_totales = Perfil.objects.aggregate(total=Sum('puntos_totales'))['total'] or 0
    
    # Top jugador del día
    top_hoy = PuntuacionDiaria.objects.filter(
        fecha=timezone.now().date()
    ).select_related('usuario').order_by('-puntos').first()
    
    return {
        'total_usuarios': total_usuarios,
        'activos_hoy': usuarios_activos_hoy,
        'puntos_totales': puntos_totales,
        'top_hoy': top_hoy,
    }

def obtener_lista_paises():
    """Lista de países para el formulario"""
    return [
        {'codigo': 'AR', 'nombre': 'Argentina'},
        {'codigo': 'BO', 'nombre': 'Bolivia'},
        {'codigo': 'BR', 'nombre': 'Brasil'},
        {'codigo': 'CL', 'nombre': 'Chile'},
        {'codigo': 'CO', 'nombre': 'Colombia'},
        {'codigo': 'CR', 'nombre': 'Costa Rica'},
        {'codigo': 'CU', 'nombre': 'Cuba'},
        {'codigo': 'DO', 'nombre': 'República Dominicana'},
        {'codigo': 'EC', 'nombre': 'Ecuador'},
        {'codigo': 'ES', 'nombre': 'España'},
        {'codigo': 'GT', 'nombre': 'Guatemala'},
        {'codigo': 'HN', 'nombre': 'Honduras'},
        {'codigo': 'MX', 'nombre': 'México'},
        {'codigo': 'NI', 'nombre': 'Nicaragua'},
        {'codigo': 'PA', 'nombre': 'Panamá'},
        {'codigo': 'PE', 'nombre': 'Perú'},
        {'codigo': 'PR', 'nombre': 'Puerto Rico'},
        {'codigo': 'PY', 'nombre': 'Paraguay'},
        {'codigo': 'SV', 'nombre': 'El Salvador'},
        {'codigo': 'UY', 'nombre': 'Uruguay'},
        {'codigo': 'VE', 'nombre': 'Venezuela'},
        {'codigo': 'US', 'nombre': 'Estados Unidos'},
    ]

def obtener_icono_categoria(categoria):
    """Obtiene el icono para una categoría de logro"""
    iconos = {
        'AVENTURA': 'map',
        'ORTOGRAFIA': 'pencil-alt',
        'SOCIAL': 'users',
        'RACHA': 'fire',
        'RANKING': 'trophy',
        'ESPECIAL': 'star',
    }
    return iconos.get(categoria, 'medal')

def obtener_fecha_inicio_ranking(periodo):
    """Obtiene la fecha de inicio según el período"""
    hoy = timezone.now().date()
    
    if periodo == 'diario':
        return hoy
    elif periodo == 'semanal':
        return hoy - timedelta(days=hoy.weekday())
    elif periodo == 'mensual':
        return hoy.replace(day=1)
    else:
        return None

def calcular_progreso_logro(user, logro):
    """Calcula el progreso de un logro específico"""
    # Implementar según el tipo de logro
    if logro.tipo == 'AVENTURA':
        completados = ProgresoAventura.objects.filter(
            usuario=user, completado=True
        ).count()
        return {
            'actual': completados,
            'necesario': logro.cantidad_necesaria,
            'porcentaje': (completados / logro.cantidad_necesaria * 100) if logro.cantidad_necesaria > 0 else 0
        }
    elif logro.tipo == 'ORTOGRAFIA':
        aciertos = ProgresoOrtografia.objects.filter(
            usuario=user
        ).aggregate(total=Sum('aciertos'))['total'] or 0
        return {
            'actual': aciertos,
            'necesario': logro.cantidad_necesaria,
            'porcentaje': (aciertos / logro.cantidad_necesaria * 100) if logro.cantidad_necesaria > 0 else 0
        }
    # ... otros tipos
    
    return {'actual': 0, 'necesario': logro.cantidad_necesaria, 'porcentaje': 0}

def calcular_proximos_logros(user, todos_logros, logros_ids):
    """Calcula los próximos logros a desbloquear"""
    proximos = []
    
    for logro in todos_logros:
        if logro.id not in logros_ids:
            progreso = calcular_progreso_logro(user, logro)
            if progreso['actual'] > 0:
                faltante = progreso['necesario'] - progreso['actual']
                proximos.append({
                    'logro': logro,
                    'progreso': progreso,
                    'faltante': faltante
                })
    
    return sorted(proximos, key=lambda x: x['faltante'])

def calcular_stats_rareza(user, todos_logros):
    """Calcula estadísticas por rareza de logros"""
    rarezas = {}
    logros_usuario = LogroDesbloqueado.objects.filter(usuario=user).values_list('logro_id', flat=True)
    
    for rareza, _ in Logro.RAREZAS:
        total = todos_logros.filter(rareza=rareza).count()
        obtenidos = todos_logros.filter(id__in=logros_usuario, rareza=rareza).count()
        
        rarezas[rareza] = {
            'total': total,
            'obtenidos': obtenidos,
            'porcentaje': (obtenidos / total * 100) if total > 0 else 0
        }
    
    return rarezas

def obtener_ayudas_disponibles(user):
    """Obtiene las ayudas disponibles del inventario"""
    items_ayuda = ItemUsuario.objects.filter(
        usuario=user,
        item__tipo='CONSUMIBLE',
        item__nombre__icontains='ayuda'
    )
    
    ayudas = {
        'pistas': 0,
        'cincuenta': 0,
        'tiempo': 0,
    }
    
    for item in items_ayuda:
        if 'pista' in item.item.nombre.lower():
            ayudas['pistas'] += item.cantidad
        elif '50' in item.item.nombre.lower():
            ayudas['cincuenta'] += item.cantidad
        elif 'tiempo' in item.item.nombre.lower():
            ayudas['tiempo'] += item.cantidad
    
    return ayudas

def nivel_esta_desbloqueado(user, nivel):
    """Verifica si un nivel está desbloqueado"""
    if nivel.orden == 1:
        return True
    
    nivel_anterior = AventuraNivel.objects.get(orden=nivel.orden - 1)
    return ProgresoAventura.objects.filter(
        usuario=user,
        nivel=nivel_anterior,
        completado=True
    ).exists()

def obtener_actividad_usuario(user, limit=10):
    """Obtiene la actividad reciente del usuario"""
    actividades = []
    
    # Actividad de aventura
    aventuras = ProgresoAventura.objects.filter(
        usuario=user
    ).order_by('-fecha_completado')[:limit]
    
    for a in aventuras:
        actividades.append({
            'tipo': 'AVENTURA',
            'descripcion': f'Completó el nivel {a.nivel.nivel}: {a.nivel.titulo}',
            'fecha': a.fecha_completado,
            'icono': 'map',
            'color': 'primary',
            'puntos': a.puntuacion,
        })
    
    # Actividad de ortografía
    ortografias = ProgresoOrtografia.objects.filter(
        usuario=user
    ).order_by('-fecha')[:limit]
    
    for o in ortografias:
        actividades.append({
            'tipo': 'ORTOGRAFIA',
            'descripcion': f'Jugó ortografía - {o.categoria}: {o.aciertos} aciertos',
            'fecha': o.fecha,
            'icono': 'pencil-alt',
            'color': 'success',
            'puntos': o.aciertos * 10,
        })
    
    # Logros desbloqueados
    logros = LogroDesbloqueado.objects.filter(
        usuario=user
    ).order_by('-fecha_desbloqueo')[:limit]
    
    for l in logros:
        actividades.append({
            'tipo': 'LOGRO',
            'descripcion': f'Desbloqueó el logro: {l.logro.nombre}',
            'fecha': l.fecha_desbloqueo,
            'icono': 'medal',
            'color': 'warning',
        })
    
    # Ordenar por fecha
    actividades.sort(key=lambda x: x['fecha'], reverse=True)
    
    return actividades[:limit]

def obtener_actividad_recente_usuario(user):
    """Obtiene actividad reciente para la vista de detalle"""
    return obtener_actividad_usuario(user, limit=20)

def obtener_posicion_usuario(user, periodo, juego):
    """Obtiene la posición del usuario en un ranking específico"""
    fecha_inicio = obtener_fecha_inicio_ranking(periodo)
    
    if fecha_inicio:
        puntuaciones = PuntuacionDiaria.objects.filter(
            fecha__gte=fecha_inicio
        ).values('usuario').annotate(
            total=Sum('puntos')
        ).order_by('-total')
        
        for idx, item in enumerate(puntuaciones, 1):
            if item['usuario'] == user.id:
                return idx
    else:
        if juego == 'todos':
            posicion = Perfil.objects.filter(
                puntos_totales__gt=user.perfil.puntos_totales
            ).count() + 1
            return posicion
    
    return None

def esta_en_linea(user):
    """Verifica si un usuario está en línea"""
    if not user.perfil.ultima_conexion:
        return False
    
    tiempo_limite = timezone.now() - timedelta(minutes=5)
    return user.perfil.ultima_conexion > tiempo_limite

def tiene_solicitud_pendiente(usuario1, usuario2):
    """Verifica si hay una solicitud pendiente entre usuarios"""
    return Amistad.objects.filter(
        (Q(usuario1=usuario1) & Q(usuario2=usuario2)) |
        (Q(usuario1=usuario2) & Q(usuario2=usuario1)),
        estado='PENDIENTE'
    ).exists()

def obtener_sugerencias_amigos(user):
    """Obtiene sugerencias de amistad basadas en intereses comunes"""
    # Usuarios que no son amigos ni tienen solicitudes pendientes
    amigos = Amistad.objects.filter(
        (Q(usuario1=user) | Q(usuario2=user)),
        estado='ACEPTADA'
    )
    
    ids_amigos = []
    for a in amigos:
        ids_amigos.append(a.usuario1.id if a.usuario2 == user else a.usuario2.id)
    ids_amigos.append(user.id)
    
    # Buscar usuarios con intereses similares (mismos juegos jugados)
    sugerencias = User.objects.exclude(id__in=ids_amigos).filter(
        progresoaventura__isnull=False
    ).distinct()[:10]
    
    return sugerencias

def obtener_conversaciones(user):
    """Obtiene las conversaciones del usuario"""
    mensajes = Mensaje.objects.filter(
        Q(remitente=user) | Q(destinatario=user)
    ).select_related('remitente', 'destinatario').order_by('-fecha_envio')
    
    conversaciones = {}
    for mensaje in mensajes:
        otro = mensaje.destinatario if mensaje.remitente == user else mensaje.remitente
        
        if otro.id not in conversaciones:
            conversaciones[otro.id] = {
                'usuario': otro,
                'ultimo_mensaje': mensaje,
                'no_leidos': Mensaje.objects.filter(
                    remitente=otro,
                    destinatario=user,
                    leido=False
                ).count()
            }
    
    return list(conversaciones.values())

def agrupar_notificaciones(notificaciones):
    """Agrupa notificaciones por fecha"""
    agrupadas = {}
    
    for notif in notificaciones:
        fecha = notif.fecha_creacion.date()
        if fecha not in agrupadas:
            agrupadas[fecha] = []
        agrupadas[fecha].append(notif)
    
    return agrupadas

def obtener_rareza_maxima(items):
    """Obtiene la rareza máxima entre los items"""
    rarezas = {'COMUN': 1, 'RARO': 2, 'EPICO': 3, 'LEGENDARIO': 4}
    max_rareza = 'COMUN'
    max_valor = 0
    
    for item in items:
        valor = rarezas.get(item.item.rareza, 0)
        if valor > max_valor:
            max_valor = valor
            max_rareza = item.item.rareza
    
    return max_rareza

def calcular_dias_activos(user):
    """Calcula los días activos del usuario"""
    return PuntuacionDiaria.objects.filter(
        usuario=user
    ).values('fecha').distinct().count()

def obtener_logros_ranking_usuario(user):
    """Obtiene logros relacionados con ranking del usuario"""
    logros = []
    posicion_global = obtener_posicion_usuario(user, 'total', 'todos')
    
    if posicion_global and posicion_global <= 10:
        logros.append({
            'nombre': 'Élite Académica',
            'descripcion': 'Estar en el Top 10 del ranking',
            'icono': 'crown',
            'color': 'warning'
        })
    
    if posicion_global == 1:
        logros.append({
            'nombre': 'Número 1',
            'descripcion': 'Ser el mejor de la academia',
            'icono': 'star',
            'color': 'danger'
        })
    
    if user.perfil.racha_maxima >= 30:
        logros.append({
            'nombre': 'Leyenda',
            'descripcion': 'Mantener racha de 30 días',
            'icono': 'fire',
            'color': 'danger'
        })
    
    return logros

def verificar_logros_aventura(user):
    """Verifica y desbloquea logros de aventura"""
    niveles_completados = ProgresoAventura.objects.filter(
        usuario=user, completado=True
    ).count()
    
    # Logro por completar todos los niveles
    total_niveles = AventuraNivel.objects.count()
    if niveles_completados == total_niveles:
        logro, _ = Logro.objects.get_or_create(
            nombre='Maestro de la Aventura',
            defaults={
                'descripcion': 'Completar todos los niveles de aventura',
                'tipo': 'AVENTURA',
                'rareza': 'LEGENDARIO',
                'icono': 'crown',
                'puntos': 1000
            }
        )
        
        if not LogroDesbloqueado.objects.filter(usuario=user, logro=logro).exists():
            LogroDesbloqueado.objects.create(
                usuario=user,
                logro=logro,
                fecha_desbloqueo=timezone.now()
            )
            
            # Notificación
            Notificacion.objects.create(
                usuario=user,
                titulo='¡Nuevo logro!',
                mensaje=f'Has desbloqueado: {logro.nombre}',
                tipo='LOGRO'
            )

def verificar_logros_ortografia(user):
    """Verifica y desbloquea logros de ortografía"""
    total_aciertos = ProgresoOrtografia.objects.filter(
        usuario=user
    ).aggregate(total=Sum('aciertos'))['total'] or 0
    
    if total_aciertos >= 1000:
        logro, _ = Logro.objects.get_or_create(
            nombre='Maestro de la Ortografía',
            defaults={
                'descripcion': 'Alcanzar 1000 aciertos en ortografía',
                'tipo': 'ORTOGRAFIA',
                'rareza': 'LEGENDARIO',
                'icono': 'pencil-alt',
                'puntos': 1000
            }
        )
        
        if not LogroDesbloqueado.objects.filter(usuario=user, logro=logro).exists():
            LogroDesbloqueado.objects.create(
                usuario=user,
                logro=logro,
                fecha_desbloqueo=timezone.now()
            )

def aplicar_efecto_item(user, item):
    """Aplica el efecto de un item consumible"""
    efectos = {
        'Pista Extra': {'tipo': 'AYUDA', 'valor': 'pista'},
        '50/50': {'tipo': 'AYUDA', 'valor': 'cincuenta'},
        'Tiempo Extra': {'tipo': 'AYUDA', 'valor': 'tiempo'},
        'Doble Puntos': {'tipo': 'BONUS', 'valor': 2},
    }
    
    return efectos.get(item.nombre, {'tipo': 'DESCONOCIDO'})