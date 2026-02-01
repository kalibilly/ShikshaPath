from django import forms
from .models import Course, CourseResource, CourseRating


class CourseCreationForm(forms.ModelForm):
    """Form for creating/editing courses."""

    class Meta:
        model = Course
        fields = ('title', 'description', 'price', 'thumbnail', 'platform_fee_percentage',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'placeholder': 'Course description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Price'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control-file'}),
            'platform_fee_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Platform fee %'}),
        }


class CourseResourceForm(forms.ModelForm):
    """Form for adding course resources (videos, PDFs, notes)."""
    
    class Meta:
        model = CourseResource
        fields = ('title', 'description', 'resource_type', 'file', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Resource description'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Display order'}),
        }


class CourseRatingForm(forms.ModelForm):
    """Form for rating and reviewing a course."""
    
    class Meta:
        model = CourseRating
        fields = ('rating', 'review')
        widgets = {
            'rating': forms.RadioSelect(choices=CourseRating.RATING_CHOICES, attrs={'class': 'form-check-input'}),
            'review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': '4', 
                'placeholder': 'Share your thoughts about this course...'
            }),
        }

