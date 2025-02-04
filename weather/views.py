from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Alert

def home(request):
    # alerts = Alert.objects.all().order_by('-date_debut')[:5] --> ca marche pas jsp
    return render(request, 'weather/home.html', {'alerts': []})

@login_required
def profile(request):
    return render(request, 'weather/profile.html')