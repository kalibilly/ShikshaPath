from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re
from .models import CustomUser


# PASSWORD STRENGTH HELPER
PASSWORD_HELP_TEXT = """
<strong>Password Requirements:</strong>
<ul style="margin: 8px 0; padding-left: 20px; font-size: 0.9em;">
    <li>Minimum 8 characters</li>
    <li>At least one uppercase letter (A-Z)</li>
    <li>At least one lowercase letter (a-z)</li>
    <li>At least one number (0-9)</li>
    <li>At least one special character (!@#$%^&*)</li>
</ul>
<strong>Example:</strong> MyPass@123
"""

def validate_password_strength(password):
    """Validate that password meets strength requirements"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&*).")
    return password


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with email/mobile options."""

    REGISTRATION_METHOD = (
        ('email', 'Register with Email'),
        ('mobile', 'Register with Mobile Number'),
    )
    
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )

    registration_method = forms.ChoiceField(
        choices=REGISTRATION_METHOD,
        initial='email',
        label='How do you want to register?',
        widget=forms.RadioSelect(attrs={'onchange': 'toggleRegistrationMethod(this.value)'})
    )
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator(message='Please enter a valid email address.')],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'id': 'email_field'
        }),
        help_text='We will send a verification link to confirm your email.'
    )
    mobile_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1-234-567-8900',
            'id': 'mobile_field',
            'style': 'display:none;'
        }),
        help_text='We will send a verification code to your mobile number.'
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='student',
        label='Register as',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doe'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        }),
        help_text=PASSWORD_HELP_TEXT
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('registration_method', 'email', 'mobile_number', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        registration_method = cleaned_data.get('registration_method')
        email = cleaned_data.get('email')
        mobile_number = cleaned_data.get('mobile_number')

        if registration_method == 'email':
            if not email:
                raise ValidationError("Please enter an email address.")
        elif registration_method == 'mobile':
            if not mobile_number:
                raise ValidationError("Please enter a mobile number.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Please enter a valid email address.")
        
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        
        return email
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile:
            return mobile
        
        # Basic mobile number validation (remove spaces and special chars)
        mobile_clean = re.sub(r'[^\d+]', '', mobile)
        
        if len(mobile_clean) < 10:
            raise ValidationError("Please enter a valid mobile number.")
        
        if CustomUser.objects.filter(mobile_number=mobile_clean).exists():
            raise ValidationError("This mobile number is already registered.")
        
        return mobile_clean

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password_strength(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        registration_method = self.cleaned_data.get('registration_method')
        
        if registration_method == 'email':
            user.username = self.cleaned_data.get('email')
            user.email = self.cleaned_data.get('email')
        else:  # mobile
            mobile = self.cleaned_data.get('mobile_number')
            # Generate email from mobile number
            user.mobile_number = mobile
            user.username = mobile
            user.email = f"mobile_{mobile}@shikshapath.local"
        
        user.is_active = False  # Deactivate until verified
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with email or mobile login."""
    username = forms.CharField(
        label='Email or Mobile Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email or mobile number',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
    )
    
    def clean(self):
        """Authenticate with email or mobile number"""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if not username or not password:
            raise forms.ValidationError('Please enter both username and password.')
        
        # Try to authenticate with email first
        from django.contrib.auth import authenticate
        
        # Try as email
        user = authenticate(username=username, password=password)
        if user is not None:
            self.user_cache = user
            return self.cleaned_data
        
        # Try as mobile number - find user by mobile then authenticate
        try:
            user_obj = CustomUser.objects.get(mobile_number=username)
            user = authenticate(username=user_obj.username, password=password)
            if user is not None:
                self.user_cache = user
                return self.cleaned_data
        except CustomUser.DoesNotExist:
            pass
        
        # If neither worked, show error
        raise forms.ValidationError('Please enter a correct username and password.')


class SendOTPForm(forms.Form):
    """Form to request OTP"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.email_verified:
                raise ValidationError("This email is already verified. You can log in directly.")
        except CustomUser.DoesNotExist:
            raise ValidationError("No account found with this email. Please register first.")
        return email


class VerifyOTPForm(forms.Form):
    """Form to verify OTP"""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='6-Digit Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'style': 'font-size: 2em; letter-spacing: 8px; font-weight: bold;',
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("OTP must contain only numbers.")
        return code


class ForgotPasswordForm(forms.Form):
    """Form to request password reset"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("No account found with this email address.")
        return email


class ResetPasswordOTPForm(forms.Form):
    """Form to verify OTP for password reset"""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='6-Digit Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'style': 'font-size: 2em; letter-spacing: 8px;',
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("Code must contain only numbers.")
        return code


class SetNewPasswordForm(forms.Form):
    """Form to set new password after OTP verification"""
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        }),
        help_text=PASSWORD_HELP_TEXT
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password'
        })
    )
    
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            validate_password_strength(password)
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password')
        password2 = cleaned_data.get('confirm_password')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        return cleaned_data


class AccountRecoveryForm(forms.Form):
    """Form to search and recover account"""
    SEARCH_BY = (
        ('first_name', 'First Name'),
        ('last_name', 'Last Name'),
        ('mobile_number', 'Mobile Number'),
    )
    
    search_by = forms.ChoiceField(
        choices=SEARCH_BY,
        label='Search account by',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search_value = forms.CharField(
        max_length=100,
        label='Search Value',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter value to search'
        })
    )
    
    def clean_search_value(self):
        value = self.cleaned_data.get('search_value')
        if not value or len(value.strip()) < 2:
            raise ValidationError("Please enter at least 2 characters.")
        return value.strip()


class VerifyEmailFromProfileForm(forms.Form):
    """Form to verify email from user profile"""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='6-Digit Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'style': 'font-size: 2em; letter-spacing: 8px;',
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("Code must contain only numbers.")
        return code


class SendMobileOTPForm(forms.Form):
    """Form to request mobile OTP"""
    mobile_number = forms.CharField(
        max_length=20,
        label='Mobile Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1-234-567-8900',
        })
    )
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        mobile_clean = re.sub(r'[^\d+]', '', mobile)
        
        if len(mobile_clean) < 10:
            raise ValidationError("Please enter a valid mobile number.")
        
        try:
            user = CustomUser.objects.get(mobile_number=mobile_clean)
            if user.phone_verified:
                raise ValidationError("This mobile number is already verified.")
        except CustomUser.DoesNotExist:
            raise ValidationError("No account found with this mobile number.")
        
        return mobile_clean


class VerifyMobileOTPForm(forms.Form):
    """Form to verify mobile OTP"""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='6-Digit Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'style': 'font-size: 2em; letter-spacing: 8px;',
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("Code must contain only numbers.")
        return code
