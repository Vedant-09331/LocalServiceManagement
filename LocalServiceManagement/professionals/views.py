from django.shortcuts import render
from .models import Professional

def professionals_list(request):

    professionals = Professional.objects.all()

    return render(request, "professionals/professionals_list.html", {
        "professionals": professionals
    })