from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserLoginForm, UserSignupForm
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from services.models import Service

def home(request):

    services = Service.objects.all()[:8]

    return render(request,"core/home.html",{
        "services":services
    })


def usersignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})


def userloginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # ROLE BASED REDIRECT
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'vendor':
                    return redirect('vendor_dashboard')
                else:
                    return redirect('user_dashboard')

            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


@login_required
def dashboard(request):
    """Redirect to the appropriate dashboard based on user role"""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'vendor':
        return redirect('vendor_dashboard')
    else:
        return redirect('user_dashboard')


@login_required
def userDashboard(request):
    if request.user.role != 'user':
        return redirect('login')
    return render(request, 'core/user_dashboard.html')


@login_required
def adminDashboard(request):
    if request.user.role != 'admin':
        return redirect('login')
    return render(request, 'core/admin_dashboard.html')


@login_required
def vendorDashboard(request):
    if request.user.role != 'vendor':
        return redirect('login')
    return render(request, 'core/vendor_dashboard.html')


def userlogoutView(request):
    logout(request)
    return redirect('login')