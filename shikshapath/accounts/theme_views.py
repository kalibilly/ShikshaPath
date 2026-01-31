"""
Theme management views
"""

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from accounts.theme_manager import get_available_themes


@login_required
@require_http_methods(["POST"])
def switch_theme(request, theme_name):
    """
    Switch user theme
    
    GET /accounts/theme/switch/<theme_name>/
    AJAX POST /accounts/theme/switch/<theme_name>/
    """
    available_themes = get_available_themes()
    
    if theme_name not in available_themes:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Invalid theme'
            }, status=400)
        messages.error(request, 'Invalid theme selected')
        return redirect('accounts:profile')
    
    # Update user theme
    request.user.theme = theme_name
    request.user.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Theme changed to {available_themes[theme_name]["name"]}',
            'theme': theme_name
        })
    
    messages.success(request, f'Theme changed to {available_themes[theme_name]["name"]}')
    return redirect('accounts:profile')


@login_required
def get_themes_api(request):
    """
    API endpoint to get all available themes
    
    GET /accounts/api/themes/
    """
    themes = get_available_themes()
    current_theme = request.user.theme if request.user.is_authenticated else 'dark'
    
    return JsonResponse({
        'success': True,
        'themes': themes,
        'current_theme': current_theme,
        'total_themes': len(themes)
    })
