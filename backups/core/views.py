from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings

def cambiar_idioma(request, idioma):
    """
    Vista para cambiar el idioma y redirigir a la página anterior
    """
    if idioma in dict(settings.LANGUAGES):
        # Activar el idioma
        activate(idioma)
        
        # Guardar en sesión
        request.session[settings.LANGUAGE_COOKIE_NAME] = idioma
        
        # Redirigir a la página anterior o al dashboard
        next_url = request.META.get('HTTP_REFERER', '/')
        
        # Extraer la URL sin el prefijo de idioma
        from django.urls import resolve
        try:
            # Si la URL actual tiene prefijo de idioma, redirigir al mismo path con nuevo idioma
            path = request.path
            for lang_code, _ in settings.LANGUAGES:
                if path.startswith(f'/{lang_code}/'):
                    path = path[len(f'/{lang_code}'):]
                    break
            return redirect(f'/{idioma}{path}')
        except:
            return redirect(next_url)
    
    return redirect('/')