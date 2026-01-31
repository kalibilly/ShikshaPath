from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, SendOTPForm, VerifyOTPForm,
    ForgotPasswordForm, ResetPasswordOTPForm, SetNewPasswordForm,
    AccountRecoveryForm, VerifyEmailFromProfileForm, SendMobileOTPForm, VerifyMobileOTPForm
)
from .models import CustomUser, OTP, MobileOTP, PasswordResetOTP
from django.contrib.auth.decorators import login_required
from .utils import send_otp, send_mobile_otp
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class RegisterView(CreateView):
    """User registration view with email verification"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:verify_otp')

    def form_valid(self, form):
        # Form already sets username = email and is_active = False
        response = super().form_valid(form)
        user = self.object
        
        # Create OTP for email verification
        otp, created = OTP.objects.get_or_create(
            user=user,
            defaults={
                'expires_at': timezone.now() + timedelta(minutes=10)
            }
        )
        
        # If OTP exists but expired, create a new one
        if not created and not otp.is_valid():
            otp.delete()
            otp = OTP.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
        
        # Send OTP email
        send_otp(user.email)
        
        # Store user email in session for confirmation page
        self.request.session['otp_email'] = user.email
        
        # Redirect to OTP verification page
        return redirect('accounts:verify_otp')


def send_otp_view(request):
    if request.method == 'POST':
        form = SendOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if send_otp(email):
                request.session['otp_email'] = email
                return redirect('verify_otp')
    else:
        form = SendOTPForm()
    return render(request, 'accounts/send_otp.html', {'form': form})


def verify_otp_view(request):
    """Verify OTP and activate user account"""
    email = request.session.get('otp_email')
    if not email:
        return redirect('accounts:send_otp')
    
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Get OTP and verify it's valid
                otp = OTP.objects.get(user__email=email, code=code)
                
                if not otp.is_valid():
                    form.add_error('code', 'OTP has expired. Please request a new one.')
                else:
                    # Mark email as verified and activate user
                    user = otp.user
                    user.email_verified = True
                    user.is_active = True
                    user.save()
                    
                    # Mark OTP as verified
                    otp.is_verified = True
                    otp.save()
                    
                    messages.success(request, "Email verified successfully! You can now log in.")
                    del request.session['otp_email']
                    return redirect('accounts:login')
            
            except OTP.DoesNotExist:
                form.add_error('code', 'Invalid OTP. Please try again.')
    else:
        form = VerifyOTPForm()
    
    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})


class CustomLoginView(LoginView):
    """Custom login view with role-based redirect and flexible email verification"""
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """Allow login but warn if email not verified"""
        user = form.get_user()
        
        # Allow login but store warning for old unverified accounts
        if not user.email_verified:
            self.request.session['needs_email_verification'] = True
            messages.warning(self.request, "⚠️ Your email is not verified. You can still access your account, but please verify your email from your profile.")
        
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect based on user role
        role = self.request.user.role
        if role == 'instructor':
            return reverse_lazy('accounts:instructor_dashboard')
        elif role == 'admin':
            return reverse_lazy('accounts:admin_dashboard')
        return reverse_lazy('home')
    

class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('home')


# Function-based view for additional features
def profile_view(request):
    """user profile view"""
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'accounts/profile.html', {'user': user})


def profile_edit_view(request):
    """Edit user profile view"""
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        return redirect('accounts:profile')

    return render(request, 'accounts/profile_edit.html', {'user': user})


def instructor_dashboard(request):
    """Instructor dashboard view"""
    if not request.user.is_authenticated or request.user.role != 'instructor':
        return redirect('accounts:login')
    
    from courses.models import Course
    courses = Course.objects.filter(instructor=request.user)
    context = {'courses': courses}
    return render(request, 'accounts/instructor_dashboard.html', context)


def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('accounts:login')
    
    return render(request, 'accounts/admin_dashboard.html')

# PASSWORD RESET VIEWS

def forgot_password_view(request):
    """Request password reset via email"""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Create password reset OTP
            otp, created = PasswordResetOTP.objects.get_or_create(
                user=user,
                defaults={'expires_at': timezone.now() + timedelta(minutes=10)}
            )
            
            # If OTP exists but expired, delete and create new one
            if not created and not otp.is_valid():
                otp.delete()
                otp = PasswordResetOTP.objects.create(
                    user=user,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
            
            # Send OTP email
            send_mail(
                subject='Password Reset OTP - ShikshaPath',
                message=f'Your password reset code is: {otp.code}\n\nThis code will expire in 10 minutes.',
                from_email='noreply@shikshapath.com',
                recipient_list=[email],
                html_message=f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2>Password Reset Request</h2>
                        <p>You requested to reset your password. Use the code below:</p>
                        <div style="background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0;">
                            <h1 style="letter-spacing: 5px; color: #333;">{otp.code}</h1>
                        </div>
                        <p><strong>This code will expire in 10 minutes.</strong></p>
                        <p>If you didn't request this, please ignore this email.</p>
                        <hr>
                        <p><small>ShikshaPath Team</small></p>
                    </body>
                </html>
                """
            )
            
            request.session['password_reset_email'] = email
            messages.success(request, f"OTP sent to {email}. Check your inbox.")
            return redirect('accounts:reset_password_otp')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_otp_view(request):
    """Verify OTP for password reset"""
    email = request.session.get('password_reset_email')
    if not email:
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                user = CustomUser.objects.get(email=email)
                otp = PasswordResetOTP.objects.get(user=user, code=code)
                
                if not otp.is_valid():
                    form.add_error('code', 'OTP has expired. Please request a new one.')
                else:
                    # Mark OTP as verified
                    otp.is_verified = True
                    otp.save()
                    
                    # Mark email as verified (bonus: verify during password reset)
                    user.email_verified = True
                    user.save()
                    
                    request.session['password_reset_verified'] = True
                    messages.success(request, "OTP verified! Now set your new password.")
                    return redirect('accounts:set_new_password')
            
            except PasswordResetOTP.DoesNotExist:
                form.add_error('code', 'Invalid OTP. Please try again.')
    else:
        form = ResetPasswordOTPForm()
    
    return render(request, 'accounts/reset_password_otp.html', {'form': form, 'email': email})


def set_new_password_view(request):
    """Set new password after OTP verification"""
    email = request.session.get('password_reset_email')
    if not email or not request.session.get('password_reset_verified'):
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                user = CustomUser.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Clean up session
                del request.session['password_reset_email']
                del request.session['password_reset_verified']
                
                messages.success(request, "✅ Password changed successfully! You can now log in with your new password.")
                return redirect('accounts:login')
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('accounts:forgot_password')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'accounts/set_new_password.html', {'form': form, 'email': email})


# ACCOUNT RECOVERY VIEW

def account_recovery_view(request):
    """Search and recover account by name or mobile number"""
    results = []
    if request.method == 'POST':
        form = AccountRecoveryForm(request.POST)
        if form.is_valid():
            search_by = form.cleaned_data['search_by']
            search_value = form.cleaned_data['search_value']
            
            if search_by == 'first_name':
                results = CustomUser.objects.filter(first_name__icontains=search_value)
            elif search_by == 'last_name':
                results = CustomUser.objects.filter(last_name__icontains=search_value)
            elif search_by == 'mobile_number':
                # Clean mobile number
                import re
                mobile_clean = re.sub(r'[^\d+]', '', search_value)
                results = CustomUser.objects.filter(mobile_number=mobile_clean)
            
            if not results:
                messages.info(request, "No accounts found matching your search.")
            else:
                messages.success(request, f"Found {results.count()} account(s).")
    else:
        form = AccountRecoveryForm()
    
    return render(request, 'accounts/account_recovery.html', {'form': form, 'results': results})


# EMAIL VERIFICATION FROM PROFILE

@login_required(login_url='accounts:login')
def verify_email_from_profile_view(request):
    """Allow users to verify email from their profile (for old unverified accounts)"""
    user = request.user
    
    if user.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = VerifyEmailFromProfileForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                otp = OTP.objects.get(user=user, code=code)
                
                if not otp.is_valid():
                    form.add_error('code', 'OTP has expired. Please request a new one.')
                else:
                    # Mark email as verified
                    user.email_verified = True
                    user.is_active = True
                    user.save()
                    
                    # Mark OTP as verified
                    otp.is_verified = True
                    otp.save()
                    
                    messages.success(request, "✅ Email verified successfully!")
                    return redirect('accounts:profile')
            
            except OTP.DoesNotExist:
                form.add_error('code', 'Invalid OTP. Please try again.')
    else:
        form = VerifyEmailFromProfileForm()
        # Send OTP
        send_otp(user.email)
        messages.info(request, f"We sent a verification code to {user.email}")
    
    return render(request, 'accounts/verify_email_from_profile.html', {'form': form, 'email': user.email})


# MOBILE VERIFICATION VIEWS

def send_mobile_otp_view(request):
    """Request mobile OTP"""
    if request.method == 'POST':
        form = SendMobileOTPForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobile_number']
            try:
                user = CustomUser.objects.get(mobile_number=mobile)
                
                # Create/get mobile OTP
                otp, created = MobileOTP.objects.get_or_create(
                    user=user,
                    defaults={'mobile_number': mobile, 'expires_at': timezone.now() + timedelta(minutes=10)}
                )
                
                if not created and not otp.is_valid():
                    otp.delete()
                    otp = MobileOTP.objects.create(
                        user=user,
                        mobile_number=mobile,
                        expires_at=timezone.now() + timedelta(minutes=10)
                    )
                
                # Send mobile OTP (will need SMS provider setup)
                send_mobile_otp(mobile, otp.code)
                
                request.session['mobile_verification'] = mobile
                messages.success(request, f"OTP sent to {mobile}")
                return redirect('accounts:verify_mobile_otp')
            except CustomUser.DoesNotExist:
                form.add_error('mobile_number', "No account found with this mobile number.")
    else:
        form = SendMobileOTPForm()
    
    return render(request, 'accounts/send_mobile_otp.html', {'form': form})


def verify_mobile_otp_view(request):
    """Verify mobile OTP"""
    mobile = request.session.get('mobile_verification')
    if not mobile:
        return redirect('accounts:send_mobile_otp')
    
    if request.method == 'POST':
        form = VerifyMobileOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                user = CustomUser.objects.get(mobile_number=mobile)
                otp = MobileOTP.objects.get(user=user, code=code)
                
                if not otp.is_valid():
                    form.add_error('code', 'OTP has expired. Please request a new one.')
                else:
                    # Mark mobile as verified
                    user.phone_verified = True
                    user.save()
                    
                    # Mark OTP as verified
                    otp.is_verified = True
                    otp.save()
                    
                    del request.session['mobile_verification']
                    messages.success(request, "✅ Mobile number verified successfully!")
                    return redirect('accounts:profile')
            
            except (CustomUser.DoesNotExist, MobileOTP.DoesNotExist):
                form.add_error('code', 'Invalid OTP. Please try again.')
    else:
        form = VerifyMobileOTPForm()
    
    return render(request, 'accounts/verify_mobile_otp.html', {'form': form, 'mobile': mobile})

@csrf_exempt
def firebase_login(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        user = authenticate(request, token=token)
        if user:
            login(request, user)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

