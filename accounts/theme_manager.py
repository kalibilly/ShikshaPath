"""
Theme Management System for ShikshaPath
Supports multiple CSS themes for different user preferences
"""

# Available themes
AVAILABLE_THEMES = {
    'dark': {
        'name': 'Dark Mode',
        'description': 'Professional dark theme',
        'primary_color': '#007bff',
        'background': '#1a1a1a',
        'text_color': '#ffffff',
        'accent': '#ff6b6b',
    },
    'light': {
        'name': 'Light Mode',
        'description': 'Clean and bright light theme',
        'primary_color': '#007bff',
        'background': '#ffffff',
        'text_color': '#000000',
        'accent': '#ff6b6b',
    },
    'gaming': {
        'name': 'Gaming Theme',
        'description': 'High contrast gaming-oriented theme',
        'primary_color': '#00ff00',
        'background': '#0a0e27',
        'text_color': '#00ff00',
        'accent': '#ff00ff',
    },
    'transparent': {
        'name': 'Transparent Glass',
        'description': 'Modern glassmorphism theme',
        'primary_color': '#ffffff',
        'background': 'rgba(20, 20, 30, 0.7)',
        'text_color': '#ffffff',
        'accent': '#00d4ff',
    },
    'pink': {
        'name': 'Pink Paradise',
        'description': 'Soft pink theme for everyone who loves pink',
        'primary_color': '#ff69b4',
        'background': '#faf0f5',
        'text_color': '#2d2d2d',
        'accent': '#ff1493',
    },
    'purple': {
        'name': 'Purple Passion',
        'description': 'Elegant purple and blue theme',
        'primary_color': '#9370db',
        'background': '#2d1b4e',
        'text_color': '#e8d5f2',
        'accent': '#c77dff',
    },
    'ocean': {
        'name': 'Ocean Blue',
        'description': 'Calm ocean-inspired theme',
        'primary_color': '#0077be',
        'background': '#0a1929',
        'text_color': '#e0f2fe',
        'accent': '#00d4ff',
    },
    'forest': {
        'name': 'Forest Green',
        'description': 'Nature-inspired green theme',
        'primary_color': '#2d5016',
        'background': '#0f2818',
        'text_color': '#d4e8d4',
        'accent': '#4ade80',
    },
    'sunset': {
        'name': 'Sunset',
        'description': 'Warm sunset colors theme',
        'primary_color': '#f97316',
        'background': '#1c0a00',
        'text_color': '#fef3c7',
        'accent': '#fbbf24',
    },
    'midnight': {
        'name': 'Midnight Blue',
        'description': 'Deep midnight blue theme',
        'primary_color': '#1e40af',
        'background': '#0c1421',
        'text_color': '#e0e7ff',
        'accent': '#60a5fa',
    },
}

def get_available_themes():
    """Returns list of all available themes"""
    return AVAILABLE_THEMES

def get_theme_by_name(theme_name):
    """Get theme configuration by name"""
    return AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES['dark'])

def get_theme_css_variables(theme_name):
    """
    Generate CSS variable declarations for a theme
    For use in stylesheet
    """
    theme = get_theme_by_name(theme_name)
    
    css = f"""
:root {{
    --theme-name: '{theme_name}';
    --primary-color: {theme['primary_color']};
    --background-color: {theme['background']};
    --text-color: {theme['text_color']};
    --accent-color: {theme['accent']};
    
    /* Derived colors */
    --primary-hover: {darken_color(theme['primary_color'], 10)};
    --background-secondary: {adjust_lightness(theme['background'], 10)};
    --border-color: {adjust_lightness(theme['text_color'], 80)};
    --shadow-color: rgba(0, 0, 0, 0.2);
}}
"""
    return css

def darken_color(hex_color, percent):
    """Darken a hex color by percentage"""
    try:
        hex_color = hex_color.lstrip('#')
        num = int(hex_color, 16)
        r = (num >> 16) & 255
        g = (num >> 8) & 255
        b = num & 255
        
        factor = 1 - (percent / 100)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    except:
        return hex_color

def adjust_lightness(color, amount):
    """Adjust lightness of color (works with rgb/rgba)"""
    # For now, return as-is
    # Can be enhanced with more sophisticated color manipulation
    return color
