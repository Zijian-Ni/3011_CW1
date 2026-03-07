from django.shortcuts import render


def dashboard(request):
    return render(request, 'dashboard.html')


def fan_portal(request):
    return render(request, 'fan_portal.html')


def admin_portal(request):
    return render(request, 'admin_portal.html')
