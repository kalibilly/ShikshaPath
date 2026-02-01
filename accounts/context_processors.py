"""
Context processors for theme system
"""

from accounts.theme_manager import get_available_themes


def theme_context(request):
    """
    Add theme information to template context
    Provides available themes and current user theme
    """
    user_theme = 'dark'  # Default theme
    
    if request.user.is_authenticated:
        user_theme = request.user.theme
    
    return {
        'available_themes': get_available_themes(),
        'current_theme': user_theme,
        'theme_count': len(get_available_themes()),
    }
