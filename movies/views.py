from django.shortcuts import render

def home(request):
    """
    Home page
    :param request:
    Url: /movies/
    """
    context = {}
    return render(request, 'home.html', context=context)
