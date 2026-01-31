from django import forms
from .models import Video


class VideoUploadForm(forms.ModelForm):
    """Form for uploading videos"""

    class Meta: 
        model = Video
        fields = ('title', 'description', 'video_file', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Video Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'order': forms.NumberInput(attrs={'class': 'form_control'}),
        }
