from django.shortcuts import render
# Create your views here.

def monument_search(request):
    return render(request, 'search_monument.html')

