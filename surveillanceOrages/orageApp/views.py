from django.shortcuts import render

def carteView(request):
    return render(request, 'orageApp/carte.html')