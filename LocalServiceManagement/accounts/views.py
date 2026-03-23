import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import OTP
from django.contrib.auth import login


# STEP 1 → Enter Email
def send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered")
            return redirect("send_otp")

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        # Save OTP
        OTP.objects.create(user=user, otp=otp_code)

        # Send Email
        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp_code}",
            "your-email@gmail.com",
            [email],
            fail_silently=False,
        )

        request.session['email'] = email
        return redirect("verify_otp")

    return render(request, "otp/send_otp.html")


# STEP 2 → Verify OTP
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        email = request.session.get('email')

        user = User.objects.get(email=email)

        otp_obj = OTP.objects.filter(user=user).last()

        # Check OTP expiry (5 minutes)
        if otp_obj.created_at < timezone.now() - timedelta(minutes=5):
            messages.error(request, "OTP expired")
            return redirect("send_otp")

        if otp_obj.otp == entered_otp:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("home")   # change if needed
        else:
            messages.error(request, "Invalid OTP")

    return render(request, "otp/verify_otp.html")