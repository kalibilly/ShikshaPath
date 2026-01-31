from django import forms
from .models import VideoGenerationTask


class VideoGenerationForm(forms.ModelForm):
    """Form for creating 3D animated videos from content"""
    
    # Add file upload field for supporting documents
    content_file = forms.FileField(
        required=False,
        label='Upload Content File (PDF, Word, PowerPoint, Excel, Text, or Video)',
        help_text='Upload PDF, Word document, PowerPoint, Excel, text file, or existing video (optional)',
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900',
            'accept': '.pdf,.doc,.docx,.txt,.pptx,.xlsx,.mp4,.avi,.mov,.mkv,.webm,.flv,.wmv,.m4v'
        })
    )
    
    class Meta:
        model = VideoGenerationTask
        fields = ('title', 'source_content', 'animation_style', 'duration', 'quality')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900',
                'placeholder': 'Video title (optional)'
            }),
            'source_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900',
                'rows': 8,
                'placeholder': 'Paste your lecture notes, script, or teaching content here...'
            }),
            'animation_style': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900',
                'min': '30',
                'max': '600',
                'step': '10'
            }),
            'quality': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-white border border-gray-300 rounded text-gray-900'
            }),
        }
        labels = {
            'source_content': 'Teaching Content',
            'animation_style': 'Animation Style',
            'duration': 'Video Duration (seconds)',
            'quality': 'Video Quality',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        source_content = cleaned_data.get('source_content')
        content_file = cleaned_data.get('content_file')
        
        # At least one content source is required
        if not source_content and not content_file:
            raise forms.ValidationError('Please provide either text content or upload a file.')
        
        # Validate file size (max 10MB)
        if content_file and content_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File size must not exceed 10MB.')
        
        return cleaned_data
